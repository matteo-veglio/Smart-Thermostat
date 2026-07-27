from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry

from .boiler_controller import BoilerController
from .climate_controller import ClimateController
from .runtime_context_factory import RuntimeContextFactory
from .state_machine import StateMachine
from .thermostat_controller import ThermostatController


@dataclass
class SmartThermostatRuntimeData:
    state_machine: StateMachine
    thermostat_controller: ThermostatController
    runtime_context_factory: RuntimeContextFactory
    boiler_controller: BoilerController
    heating_climate_controller: ClimateController
    cooling_climate_controller: ClimateController


type SmartThermostatConfigEntry = ConfigEntry[SmartThermostatRuntimeData]
