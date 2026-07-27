from enum import Enum

from .runtime_context import RuntimeContext
from .state_machine import ThermostatState


class Demand(Enum):
    NO_DEMAND = "no_demand"
    HEATING = "heating"
    COOLING = "cooling"


class DemandEngine:
    def evaluate_demand(self, context: RuntimeContext) -> Demand:
        if context.current_state == ThermostatState.HEATING:
            if context.current_temperature < context.heating_target_temperature:
                return Demand.HEATING
        elif context.current_temperature <= context.heating_target_temperature - context.hysteresis:
            return Demand.HEATING

        if context.current_state == ThermostatState.COOLING:
            if context.current_temperature > context.cooling_target_temperature:
                return Demand.COOLING
        elif context.current_temperature >= context.cooling_target_temperature + context.hysteresis:
            return Demand.COOLING

        return Demand.NO_DEMAND
