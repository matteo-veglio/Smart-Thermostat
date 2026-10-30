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
                # specs/12_controller_protection_workflow.md §4: Minimum Runtime protects
                # only the Climate Device (air conditioner) against frequent compressor
                # cycling. The Boiler has no equivalent physical constraint, so replacing
                # it with a different source is never gated by Minimum Runtime.
                applies_minimum_runtime = context.current_heating_source == HeatingSource.AIR_CONDITIONER

                minimum_runtime_permission = (
                    self._protection_engine.evaluate_minimum_runtime(context)
                    if applies_minimum_runtime
                    else Permission.ALLOWED
                )

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
            # specs/12_controller_protection_workflow.md §3: both Minimum Runtime and
            # Shutdown Delay protect the Climate Device (air conditioner) only. The
            # Boiler has no equivalent cycling constraint, and radiator-based heating
            # already has significant thermal inertia, so keeping it running after
            # demand has ended (or after being told to stop) would only cause
            # unnecessary overshoot - the Boiler stops immediately once no other
            # applicable condition blocks it. This branch handles both a completed
            # shutdown (STOPPING -> IDLE) and a cancelled startup (STARTING -> IDLE) -
            # the Climate Device may already have been commanded on during STARTING, so
            # the same protections apply identically regardless of origin.
            if current_state in (ThermostatState.STOPPING, ThermostatState.STARTING) and (
                requested_state == ThermostatState.IDLE
            ):
                active_source_is_climate_device = context.current_operation == CurrentOperation.COOLING or (
                    context.current_operation == CurrentOperation.HEATING
                    and context.current_heating_source == HeatingSource.AIR_CONDITIONER
                )

                minimum_runtime_permission = (
                    self._protection_engine.evaluate_minimum_runtime(context)
                    if active_source_is_climate_device
                    else Permission.ALLOWED
                )

                if minimum_runtime_permission == Permission.ALLOWED:
                    # specs/21_external_state_transitions.md §4: Shutdown Delay only ever
                    # applies to an *automatic* shutdown (demand ending while the
                    # thermostat remains enabled). An explicit user OFF request
                    # (enabled=False) bypasses Shutdown Delay entirely - Minimum Runtime
                    # remains the only protection that may still delay it, and only for
                    # the Climate Device.
                    applies_shutdown_delay = enabled and active_source_is_climate_device

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

                # specs/11_controller_transition_table.md §8 / specs/12_controller_protection_workflow.md
                # §3 STOPPING -> STARTING: if demand returns before the pending shutdown
                # completes, the shutdown is cancelled. The controlled device was never
                # actually told to stop (specs/17/§18 device actions only reach the "off"
                # state once IDLE is reached), so - unlike STOPPING -> IDLE - no protection
                # check applies here: neither Minimum Runtime nor Shutdown Delay gate a
                # resumption of an operation that never stopped. This transition is
                # intentionally immediate and ungated.
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
        # `device_stopped` marks the exact instant STOPPING -> IDLE completes: the
        # controlled device has now fully stopped and any future demand starts a new,
        # independent regulation episode. Without this, a demand that ends and later
        # resumes (even with the same operation and the same source) would silently
        # inherit I_prev/Desat_prev from the episode that already completed - the
        # STARTING/STOPPING *pause* is momentary and correctly preserves state, but a
        # full stop all the way to IDLE is not a pause, it is the episode ending.
        climate_regulation_reset_required = (
            not enabled
            or device_stopped
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
        # Climate Regulation tracks whether the Climate Device is physically active, not
        # merely whether the logical Thermostat State is HEATING/COOLING. For Cooling,
        # the Climate Device is already commanded on during STARTING (the physical ON/
        # mode/target actions are generated the moment STARTING is entered - see
        # _generate_device_actions) and remains commanded on throughout STOPPING (the
        # controlled device is never told to stop until IDLE is actually reached - see
        # specs/12_controller_protection_workflow.md §3). Regulation must therefore stay
        # active across both, so the PI keeps adapting the Climate Device target to the
        # current room temperature/error for as long as the device is genuinely on -
        # including the entire Minimum Runtime / Shutdown Delay window - and only stops
        # once the device is actually turned off (STOPPING -> IDLE completes). Heating's
        # own condition is deliberately left unchanged: this widening applies only when
        # the requested operation is COOLING.
        regulation_active = uses_climate_device and (
            effective_state in (ThermostatState.HEATING, ThermostatState.COOLING)
            or (
                requested_operation == CurrentOperation.COOLING
                and effective_state in (ThermostatState.STARTING, ThermostatState.STOPPING)
            )
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
            if demand == Demand.HEATING:
                return CurrentOperation.HEATING

            if demand == Demand.COOLING:
                return CurrentOperation.COOLING

            # NO_DEMAND while still STARTING (e.g. Minimum Runtime denying STARTING ->
            # IDLE): preserve the operation actually in progress instead of defaulting to
            # COOLING - mirrors the STOPPING branch immediately below.
            return context.current_operation

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
        elif (
            current_state == ThermostatState.STARTING
            and demand == Demand.NO_DEMAND
            and context.demand_ended_at == 0.0
        ):
            # Write-once, guarded on the existing "0.0 means unset" sentinel: unlike
            # HEATING/COOLING (which always transition away from themselves the instant
            # NO_DEMAND is observed), STARTING can remain STARTING across many
            # consecutive NO_DEMAND evaluations while Minimum Runtime denies STARTING ->
            # IDLE. Without this guard the timestamp would be pushed forward every cycle
            # and Shutdown Delay would never elapse.
            self._runtime_state.demand_ended_at = context.now
        elif requested_state == ThermostatState.STARTING:
            self._runtime_state.demand_ended_at = 0.0

        # specs/15_runtime_state_update_rules.md §4 Device Started At
        # The physical ON command is issued the instant IDLE -> STARTING is entered
        # (_generate_device_actions), not at STARTING -> HEATING/COOLING confirmation, so
        # the episode's runtime timer must be anchored there for Minimum Runtime to
        # measure the actual physical start.
        # specs/12_controller_protection_workflow.md §3 STOPPING -> STARTING: a cancelled
        # shutdown (STOPPING -> STARTING -> HEATING/COOLING) must never look like a fresh
        # physical start - the device was never told to stop, so its original start time
        # must be preserved. `context.device_started_at` is only ever 0.0 immediately
        # after a real stop (STOPPING -> IDLE / STARTING -> IDLE) or before the very
        # first start; guarding on it distinguishes a genuine start (resets the timer)
        # from a resumed one (leaves the original timer untouched), without requiring any
        # new state or execution path.
        if current_state == ThermostatState.IDLE and requested_state == ThermostatState.STARTING:
            self._runtime_state.device_started_at = context.now
        elif (
            current_state == ThermostatState.STARTING
            and requested_state in (ThermostatState.HEATING, ThermostatState.COOLING)
            and context.device_started_at == 0.0
        ):
            self._runtime_state.device_started_at = context.now
        elif device_stopped:
            self._runtime_state.device_started_at = 0.0

        # specs/15_runtime_state_update_rules.md §4 Current Operation
        self._runtime_state.current_operation = requested_operation
