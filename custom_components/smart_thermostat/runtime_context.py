from dataclasses import dataclass

from .source_engine import HeatingSource
from .state_machine import ThermostatState


@dataclass(frozen=True)
class RuntimeContext:
    # Thermostat State
    current_state: ThermostatState

    # Heating Source
    current_heating_source: HeatingSource

    # Environment
    current_temperature: float
    current_humidity: float

    # User Configuration
    heating_target_temperature: float
    cooling_target_temperature: float
    hysteresis: float

    # Energy
    instantaneous_energy_surplus: float
    minimum_energy_surplus: float

    # Protection Timing
    now: float
    device_started_at: float
    demand_ended_at: float
    source_selected_at: float
    desired_source_differs_since: float

    # Protection Configuration
    minimum_device_runtime: float
    minimum_source_runtime: float
    shutdown_delay: float
    source_change_delay: float
