from dataclasses import dataclass

from .demand_engine import Demand, DemandEngine
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
    current_state: ThermostatState
    requested_state: ThermostatState
    protection_result: Permission | None


class ThermostatController:
    def __init__(
        self,
        state_machine: StateMachine,
        demand_engine: DemandEngine,
        source_engine: SourceEngine,
        protection_engine: ProtectionEngine,
        transition_table: TransitionTable,
        runtime_state: ThermostatRuntimeState,
    ) -> None:
        self._state_machine = state_machine
        self._demand_engine = demand_engine
        self._source_engine = source_engine
        self._protection_engine = protection_engine
        self._transition_table = transition_table
        self._runtime_state = runtime_state

    def evaluate(self, context: RuntimeContext) -> ThermostatControllerResult:
        current_state = context.current_state

        demand = self._demand_engine.evaluate_demand(context)

        protection_result: Permission | None = None
        requested_heating_source: HeatingSource | None = None
        source_change_effective = False

        if demand == Demand.HEATING:
            requested_heating_source = self._source_engine.evaluate_source(context)

            if requested_heating_source != context.current_heating_source:
                source_runtime_permission = self._protection_engine.evaluate_minimum_source_runtime(context)

                if source_runtime_permission == Permission.ALLOWED:
                    protection_result = self._protection_engine.evaluate_source_change_delay(context)

                    if protection_result == Permission.ALLOWED:
                        source_change_effective = True
                else:
                    protection_result = source_runtime_permission

        requested_state = self._transition_table.resolve_requested_state(current_state, demand)

        device_stopped = False

        if requested_state != current_state:
            if current_state == ThermostatState.STOPPING and requested_state == ThermostatState.IDLE:
                device_runtime_permission = self._protection_engine.evaluate_minimum_device_runtime(context)

                if device_runtime_permission == Permission.ALLOWED:
                    protection_result = self._protection_engine.evaluate_shutdown_delay(context)
                else:
                    protection_result = device_runtime_permission

                if protection_result == Permission.ALLOWED:
                    self._state_machine.transition_to(requested_state)
                    device_stopped = True
            else:
                self._state_machine.transition_to(requested_state)

        self._update_runtime_state(
            context=context,
            current_state=current_state,
            demand=demand,
            requested_state=requested_state,
            requested_heating_source=requested_heating_source,
            source_change_effective=source_change_effective,
            device_stopped=device_stopped,
        )

        return ThermostatControllerResult(
            demand=demand,
            current_heating_source=self._runtime_state.current_heating_source,
            requested_heating_source=requested_heating_source,
            current_operation=self._runtime_state.current_operation,
            current_state=self._state_machine.current_state,
            requested_state=requested_state,
            protection_result=protection_result,
        )

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
        if requested_state == ThermostatState.STARTING and demand == Demand.HEATING:
            self._runtime_state.current_operation = CurrentOperation.HEATING
        elif requested_state == ThermostatState.STARTING and demand == Demand.COOLING:
            self._runtime_state.current_operation = CurrentOperation.COOLING
        elif device_stopped:
            self._runtime_state.current_operation = CurrentOperation.NONE
