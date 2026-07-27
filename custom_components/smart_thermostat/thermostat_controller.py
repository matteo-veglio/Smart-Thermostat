from dataclasses import dataclass

from .demand_engine import Demand, DemandEngine
from .protection_engine import Permission, ProtectionEngine
from .runtime_context import RuntimeContext
from .source_engine import HeatingSource, SourceEngine
from .state_machine import StateMachine, ThermostatState
from .transition_table import TransitionTable


@dataclass(frozen=True)
class ThermostatControllerResult:
    demand: Demand
    current_heating_source: HeatingSource
    requested_heating_source: HeatingSource | None
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
    ) -> None:
        self._state_machine = state_machine
        self._demand_engine = demand_engine
        self._source_engine = source_engine
        self._protection_engine = protection_engine
        self._transition_table = transition_table

    def evaluate(self, context: RuntimeContext) -> ThermostatControllerResult:
        current_state = context.current_state

        demand = self._demand_engine.evaluate_demand(context)

        protection_result: Permission | None = None
        requested_heating_source: HeatingSource | None = None

        if demand == Demand.HEATING:
            requested_heating_source = self._source_engine.evaluate_source(context)

            if requested_heating_source != context.current_heating_source:
                source_runtime_permission = self._protection_engine.evaluate_minimum_source_runtime(context)

                if source_runtime_permission == Permission.ALLOWED:
                    protection_result = self._protection_engine.evaluate_source_change_delay(context)
                else:
                    protection_result = source_runtime_permission

        requested_state = self._transition_table.resolve_requested_state(current_state, demand)

        if requested_state != current_state:
            if current_state == ThermostatState.STOPPING and requested_state == ThermostatState.IDLE:
                device_runtime_permission = self._protection_engine.evaluate_minimum_device_runtime(context)

                if device_runtime_permission == Permission.ALLOWED:
                    protection_result = self._protection_engine.evaluate_shutdown_delay(context)
                else:
                    protection_result = device_runtime_permission

                if protection_result == Permission.ALLOWED:
                    self._state_machine.transition_to(requested_state)
            else:
                self._state_machine.transition_to(requested_state)

        return ThermostatControllerResult(
            demand=demand,
            current_heating_source=context.current_heating_source,
            requested_heating_source=requested_heating_source,
            current_state=self._state_machine.current_state,
            requested_state=requested_state,
            protection_result=protection_result,
        )
