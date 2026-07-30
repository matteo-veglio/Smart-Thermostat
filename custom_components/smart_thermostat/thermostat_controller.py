import math
from dataclasses import dataclass

from .climate_control_algorithm import ClimateControlAlgorithm
from .demand_engine import Demand, DemandEngine
from .device_action import (
    ClimateHVACMode,
    DeviceAction,
    PowerState,
    SetClimateHVACMode,
    SetClimateTargetTemperature,
    TurnBoilerOff,
    TurnBoilerOn,
    TurnClimateOff,
    TurnClimateOn,
)
from .protection_engine import Permission, ProtectionEngine
from .runtime_context import RuntimeContext
from .source_engine import HeatingSource, SourceEngine
from .state_machine import StateMachine, ThermostatState
from .thermostat_runtime_state import CurrentOperation, ThermostatRuntimeState
from .transition_table import TransitionTable


@dataclass(frozen=True)
class ThermostatControllerResult:
    demand: Demand
    current_heating_source: HeatingSource
    requested_heating_source: HeatingSource | None
    current_operation: CurrentOperation
    requested_operation: CurrentOperation
    current_state: ThermostatState
    requested_state: ThermostatState
    protection_result: Permission | None
    requested_device_actions: tuple[DeviceAction, ...]
    # specs/22_scheduled_evaluation_workflow.md §3 ThermostatControllerResult
    next_evaluation_at: float | None = None
    # specs/27_climate_control_architecture.md §6 Activation Conditions / §11 Evaluation
    # Workflow: whether the dedicated 30-second Climate Regulation scheduler should be
    # running right now. This is a passive observation of this cycle's activation
    # decision - it never triggers a PI iteration itself.
    climate_regulation_active: bool = False


class ThermostatController:
    def __init__(
        self,
        state_machine: StateMachine,
        demand_engine: DemandEngine,
        source_engine: SourceEngine,
        protection_engine: ProtectionEngine,
        transition_table: TransitionTable,
        runtime_state: ThermostatRuntimeState,
        climate_control_algorithm: ClimateControlAlgorithm,
    ) -> None:
        self._state_machine = state_machine
        self._demand_engine = demand_engine
        self._source_engine = source_engine
        self._protection_engine = protection_engine
        self._transition_table = transition_table
        self._runtime_state = runtime_state
        self._climate_control_algorithm = climate_control_algorithm

    def evaluate(
        self,
        context: RuntimeContext,
        *,
        enabled: bool = True,
    ) -> ThermostatControllerResult:
        current_state = context.current_state

        demand = self._demand_engine.evaluate_demand(context) if enabled else Demand.NO_DEMAND

        protection_result: Permission | None = None
        requested_heating_source: HeatingSource | None = None
        source_change_effective = False
        # specs/22_scheduled_evaluation_workflow.md §2 Thermostat Controller Responsibility
        next_evaluation_at: float | None = None

        if demand == Demand.HEATING:
            requested_heating_source = self._source_engine.evaluate_source(context)

            if requested_heating_source != context.current_heating_source:
                minimum_runtime_permission = self._protection_engine.evaluate_minimum_runtime(context)

                if minimum_runtime_permission == Permission.ALLOWED:
                    protection_result = self._protection_engine.evaluate_source_change_delay(context)

                    if protection_result == Permission.ALLOWED:
                        source_change_effective = True
                    else:
                        next_evaluation_at = self._earliest_allowed_instant(
                            context.desired_source_differs_since, context.source_change_delay
                        )
                else:
                    protection_result = minimum_runtime_permission
                    next_evaluation_at = self._earliest_allowed_instant(
                        context.device_started_at, context.minimum_runtime
                    )

        requested_state = self._transition_table.resolve_requested_state(current_state, demand)

        device_stopped = False

        if requested_state != current_state:
            if current_state == ThermostatState.STOPPING and requested_state == ThermostatState.IDLE:
                minimum_runtime_permission = self._protection_engine.evaluate_minimum_runtime(context)

                if minimum_runtime_permission == Permission.ALLOWED:
                    # Shutdown Delay only applies while the Climate Device is the active
                    # heating/cooling solution. Radiator-based Boiler heating already has
                    # significant thermal inertia, so keeping it running after demand has
                    # ended would only cause unnecessary overshoot - the Boiler stops
                    # immediately once Minimum Runtime is satisfied.
                    applies_shutdown_delay = context.current_operation == CurrentOperation.COOLING or (
                        context.current_operation == CurrentOperation.HEATING
                        and context.current_heating_source == HeatingSource.AIR_CONDITIONER
                    )

                    protection_result = (
                        self._protection_engine.evaluate_shutdown_delay(context)
                        if applies_shutdown_delay
                        else Permission.ALLOWED
                    )
                else:
                    protection_result = minimum_runtime_permission

                if protection_result == Permission.ALLOWED:
                    self._state_machine.transition_to(requested_state)
                    device_stopped = True
                elif minimum_runtime_permission == Permission.DENIED:
                    next_evaluation_at = self._earliest_allowed_instant(
                        context.device_started_at, context.minimum_runtime
                    )
                else:
                    next_evaluation_at = self._earliest_allowed_instant(
                        context.demand_ended_at, context.shutdown_delay
                    )
            else:
                # specs/22_scheduled_evaluation_workflow.md §2 Thermostat Controller Responsibility
                # HEATING -> STOPPING / COOLING -> STOPPING: the Protection Rules governing
                # STOPPING -> IDLE are only evaluated once the Thermostat State is already
                # STOPPING, so request one immediate follow-up evaluation. Gating this on the
                # *current* (pre-transition) state guarantees it fires at most once per
                # transition into STOPPING - the next evaluation will observe current_state
                # already equal to STOPPING and will never re-enter this branch.
                if current_state in (ThermostatState.HEATING, ThermostatState.COOLING) and (
                    requested_state == ThermostatState.STOPPING
                ):
                    next_evaluation_at = context.now

                self._state_machine.transition_to(requested_state)

        # specs/21_external_state_transitions.md §4 Disabling the Thermostat
        if not enabled and self._state_machine.current_state == ThermostatState.IDLE:
            self._state_machine.transition_to(ThermostatState.OFF)

        effective_state = self._state_machine.current_state

        requested_operation = self._determine_requested_operation(
            effective_state=effective_state,
            demand=demand,
            context=context,
        )

        self._update_runtime_state(
            context=context,
            current_state=current_state,
            demand=demand,
            requested_state=requested_state,
            requested_heating_source=requested_heating_source,
            source_change_effective=source_change_effective,
            device_stopped=device_stopped,
            requested_operation=requested_operation,
        )

        effective_heating_source = self._runtime_state.current_heating_source

        # specs/27_climate_control_architecture.md §10 Reset Behaviour
        # Reset only on the specific transitions this document names - never merely
        # because regulation is momentarily paused (STARTING/STOPPING, see below).
        climate_regulation_reset_required = (
            not enabled
            or (
                context.current_operation == CurrentOperation.HEATING
                and context.current_heating_source == HeatingSource.AIR_CONDITIONER
                and effective_heating_source == HeatingSource.BOILER
            )
            or (context.current_operation == CurrentOperation.HEATING and requested_operation == CurrentOperation.COOLING)
            or (context.current_operation == CurrentOperation.COOLING and requested_operation == CurrentOperation.HEATING)
        )

        if climate_regulation_reset_required:
            self._climate_control_algorithm.reset()

        target_temperature: float | None = None
        uses_climate_device = requested_operation == CurrentOperation.COOLING or (
            requested_operation == CurrentOperation.HEATING
            and effective_heating_source == HeatingSource.AIR_CONDITIONER
        )

        # specs/27_climate_control_architecture.md §6 Activation Conditions
        regulation_active = uses_climate_device and effective_state in (
            ThermostatState.HEATING,
            ThermostatState.COOLING,
        )

        # Control Diagnostics: a passive observation of this cycle's activation
        # decision. This never influences the decision itself or any equation above.
        self._climate_control_algorithm.update_controller_enabled(regulation_active)

        if uses_climate_device:
            # specs/27_climate_control_architecture.md §11 Evaluation Workflow: the PI
            # controller is never invoked from this event-driven path, regardless of
            # whether regulation is active or momentarily paused (STARTING/STOPPING).
            # It is evaluated exclusively by the dedicated 30-second scheduler owned by
            # the Climate Entity. This method only ever reads whatever output that
            # scheduler last produced.
            target_temperature = self._climate_control_algorithm.last_output

            if target_temperature is None:
                target_temperature = context.current_climate_target_temperature

        requested_device_actions = self._generate_device_actions(
            requested_operation=requested_operation,
            effective_heating_source=effective_heating_source,
            uses_climate_device=uses_climate_device,
            target_temperature=target_temperature,
            context=context,
        )

        return ThermostatControllerResult(
            demand=demand,
            current_heating_source=self._runtime_state.current_heating_source,
            requested_heating_source=requested_heating_source,
            current_operation=self._runtime_state.current_operation,
            requested_operation=requested_operation,
            current_state=self._state_machine.current_state,
            requested_state=requested_state,
            protection_result=protection_result,
            requested_device_actions=requested_device_actions,
            next_evaluation_at=next_evaluation_at,
            climate_regulation_active=regulation_active,
        )

    @staticmethod
    def _earliest_allowed_instant(reference_timestamp: float, required_delay: float) -> float:
        # specs/22_scheduled_evaluation_workflow.md §2 Thermostat Controller Responsibility
        return reference_timestamp + required_delay

    def _determine_requested_operation(
        self,
        *,
        effective_state: ThermostatState,
        demand: Demand,
        context: RuntimeContext,
    ) -> CurrentOperation:
        # specs/10_controller_workflow.md §4 Requested Operation
        if effective_state in (ThermostatState.OFF, ThermostatState.IDLE):
            return CurrentOperation.NONE

        if effective_state == ThermostatState.STARTING:
            return CurrentOperation.HEATING if demand == Demand.HEATING else CurrentOperation.COOLING

        if effective_state == ThermostatState.HEATING:
            return CurrentOperation.HEATING

        if effective_state == ThermostatState.COOLING:
            return CurrentOperation.COOLING

        # STOPPING: the controlled device keeps performing the operation already active.
        return context.current_operation

    def _generate_device_actions(
        self,
        *,
        requested_operation: CurrentOperation,
        effective_heating_source: HeatingSource,
        uses_climate_device: bool,
        target_temperature: float | None,
        context: RuntimeContext,
    ) -> tuple[DeviceAction, ...]:
        actions: list[DeviceAction] = []

        desired_boiler_power = (
            PowerState.ON
            if requested_operation == CurrentOperation.HEATING and effective_heating_source == HeatingSource.BOILER
            else PowerState.OFF
        )

        if desired_boiler_power != context.current_boiler_power_state:
            actions.append(TurnBoilerOn() if desired_boiler_power == PowerState.ON else TurnBoilerOff())

        if uses_climate_device:
            desired_hvac_mode = (
                ClimateHVACMode.HEAT if requested_operation == CurrentOperation.HEATING else ClimateHVACMode.COOL
            )

            if context.current_climate_power_state != PowerState.ON:
                actions.append(TurnClimateOn())

            if context.current_climate_hvac_mode != desired_hvac_mode:
                actions.append(SetClimateHVACMode(desired_hvac_mode))

            # The Climate Control Algorithm (specs/28) computes TAc with full
            # floating-point precision and is never touched here. Only the value sent
            # to the physical Climate Device is rounded to the nearest integer, and
            # only when that rounded value actually differs from the device's current
            # reported target does a command get generated - avoiding redundant
            # commands every time TAc changes by a fraction of a degree.
            rounded_target_temperature = self._round_climate_target_temperature(target_temperature)

            if (
                rounded_target_temperature is not None
                and context.current_climate_target_temperature != rounded_target_temperature
            ):
                actions.append(SetClimateTargetTemperature(rounded_target_temperature))
        elif context.current_climate_power_state != PowerState.OFF:
            actions.append(TurnClimateOff())

        return tuple(actions)

    @staticmethod
    def _round_climate_target_temperature(target_temperature: float | None) -> float | None:
        if target_temperature is None:
            return None

        # Standard "round half up" (decimal part >= 0.5 rounds up), not Python's
        # built-in banker's rounding.
        return float(math.floor(target_temperature + 0.5))

    def _update_runtime_state(
        self,
        *,
        context: RuntimeContext,
        current_state: ThermostatState,
        demand: Demand,
        requested_state: ThermostatState,
        requested_heating_source: HeatingSource | None,
        source_change_effective: bool,
        device_stopped: bool,
        requested_operation: CurrentOperation,
    ) -> None:
        # specs/15_runtime_state_update_rules.md §3 Current Heating Source
        # specs/15_runtime_state_update_rules.md §6 Source Selected At
        if source_change_effective:
            self._runtime_state.current_heating_source = requested_heating_source
            self._runtime_state.source_selected_at = context.now

        # specs/15_runtime_state_update_rules.md §7 Desired Source Differs Since
        if requested_heating_source is not None:
            effective_current_heating_source = (
                requested_heating_source if source_change_effective else context.current_heating_source
            )

            if requested_heating_source != effective_current_heating_source:
                if self._runtime_state.desired_source_differs_since == 0.0:
                    self._runtime_state.desired_source_differs_since = context.now
            else:
                self._runtime_state.desired_source_differs_since = 0.0
        else:
            self._runtime_state.desired_source_differs_since = 0.0

        # specs/15_runtime_state_update_rules.md §5 Demand Ended At
        if current_state in (ThermostatState.HEATING, ThermostatState.COOLING) and demand == Demand.NO_DEMAND:
            self._runtime_state.demand_ended_at = context.now
        elif requested_state == ThermostatState.STARTING:
            self._runtime_state.demand_ended_at = 0.0

        # specs/15_runtime_state_update_rules.md §4 Device Started At
        if current_state == ThermostatState.STARTING and requested_state in (
            ThermostatState.HEATING,
            ThermostatState.COOLING,
        ):
            self._runtime_state.device_started_at = context.now
        elif device_stopped:
            self._runtime_state.device_started_at = 0.0

        # specs/15_runtime_state_update_rules.md §4 Current Operation
        self._runtime_state.current_operation = requested_operation
