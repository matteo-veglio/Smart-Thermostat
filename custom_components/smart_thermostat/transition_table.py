from .demand_engine import Demand
from .state_machine import ThermostatState

_TRANSITIONS: dict[tuple[ThermostatState, Demand], ThermostatState] = {
    (ThermostatState.OFF, Demand.NO_DEMAND): ThermostatState.OFF,
    (ThermostatState.OFF, Demand.HEATING): ThermostatState.OFF,
    (ThermostatState.OFF, Demand.COOLING): ThermostatState.OFF,
    (ThermostatState.IDLE, Demand.NO_DEMAND): ThermostatState.IDLE,
    (ThermostatState.IDLE, Demand.HEATING): ThermostatState.STARTING,
    (ThermostatState.IDLE, Demand.COOLING): ThermostatState.STARTING,
    (ThermostatState.STARTING, Demand.NO_DEMAND): ThermostatState.IDLE,
    (ThermostatState.STARTING, Demand.HEATING): ThermostatState.HEATING,
    (ThermostatState.STARTING, Demand.COOLING): ThermostatState.COOLING,
    (ThermostatState.HEATING, Demand.NO_DEMAND): ThermostatState.STOPPING,
    (ThermostatState.HEATING, Demand.HEATING): ThermostatState.HEATING,
    (ThermostatState.HEATING, Demand.COOLING): ThermostatState.STOPPING,
    (ThermostatState.COOLING, Demand.NO_DEMAND): ThermostatState.STOPPING,
    (ThermostatState.COOLING, Demand.COOLING): ThermostatState.COOLING,
    (ThermostatState.COOLING, Demand.HEATING): ThermostatState.STOPPING,
    (ThermostatState.STOPPING, Demand.NO_DEMAND): ThermostatState.IDLE,
    (ThermostatState.STOPPING, Demand.HEATING): ThermostatState.STARTING,
    (ThermostatState.STOPPING, Demand.COOLING): ThermostatState.STARTING,
}


class TransitionTable:
    def resolve_requested_state(
        self,
        current_state: ThermostatState,
        demand: Demand,
    ) -> ThermostatState:
        return _TRANSITIONS[(current_state, demand)]
