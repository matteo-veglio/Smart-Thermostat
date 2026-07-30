from enum import Enum

from .runtime_context import RuntimeContext
from .state_machine import ThermostatState


class Demand(Enum):
    NO_DEMAND = "no_demand"
    HEATING = "heating"
    COOLING = "cooling"


class DemandEngine:
    def evaluate_demand(self, context: RuntimeContext) -> Demand:
        # specs/05_control_algorithm.md §5 Symmetric Hysteresis Principle: once a demand
        # has started it remains active until the *opposite* hysteresis threshold is
        # crossed - crossing the target temperature alone never ends it.
        if context.current_state == ThermostatState.HEATING:
            if context.current_temperature < context.heating_target_temperature + context.hysteresis:
                return Demand.HEATING
        elif context.current_temperature <= context.heating_target_temperature - context.hysteresis:
            return Demand.HEATING

        if context.current_state == ThermostatState.COOLING:
            if context.current_temperature > context.cooling_target_temperature - context.hysteresis:
                return Demand.COOLING
        elif context.current_temperature >= context.cooling_target_temperature + context.hysteresis:
            return Demand.COOLING

        return Demand.NO_DEMAND
