from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry

from .boiler_controller import BoilerController
from .climate_control_algorithm import ClimateControlAlgorithm
from .climate_controller import ClimateController
from .runtime_context_factory import RuntimeContextFactory
from .state_machine import StateMachine
from .thermostat_controller import ThermostatController
from .thermostat_runtime_state import ThermostatRuntimeState


@dataclass
class SmartThermostatRuntimeData:
    state_machine: StateMachine
    runtime_state: ThermostatRuntimeState
    thermostat_controller: ThermostatController
    runtime_context_factory: RuntimeContextFactory
    climate_controller: ClimateController
    # specs/24_configuration_flow.md §4 Devices Step: the Boiler is mandatory.
    boiler_controller: BoilerController
    # Control Diagnostics feature: shared read access for the sensor platform, so it
    # never needs to reach through ThermostatController's private internals.
    climate_control_algorithm: ClimateControlAlgorithm
    # Mirrors the Climate Entity's own availability so diagnostic sensors can follow the
    # Smart Thermostat's lifecycle without recomputing anything themselves.
    climate_entity_available: bool = True


type SmartThermostatConfigEntry = ConfigEntry[SmartThermostatRuntimeData]
