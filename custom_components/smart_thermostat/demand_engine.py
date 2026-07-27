from enum import Enum

from .state_machine import ThermostatState


class Demand(Enum):
    NO_DEMAND = "no_demand"
    HEATING = "heating"
    COOLING = "cooling"


class DemandEngine:
    def evaluate_demand(
        self,
        current_temperature: float,
        heating_target_temperature: float,
        cooling_target_temperature: float,
        hysteresis: float,
        current_state: ThermostatState,
    ) -> Demand:
        if current_state == ThermostatState.HEATING:
            if current_temperature < heating_target_temperature:
                return Demand.HEATING
        elif current_temperature <= heating_target_temperature - hysteresis:
            return Demand.HEATING

        if current_state == ThermostatState.COOLING:
            if current_temperature > cooling_target_temperature:
                return Demand.COOLING
        elif current_temperature >= cooling_target_temperature + hysteresis:
            return Demand.COOLING

        return Demand.NO_DEMAND
