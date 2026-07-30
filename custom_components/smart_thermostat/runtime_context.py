from dataclasses import dataclass

from .device_action import ClimateHVACMode, PowerState
from .source_engine import HeatingSource
from .state_machine import ThermostatState
from .thermostat_runtime_state import CurrentOperation


@dataclass(frozen=True)
class RuntimeContext:
    # Thermostat State
    current_state: ThermostatState

    # Environment
    current_temperature: float
    current_humidity: float | None

    # User Configuration
    heating_target_temperature: float
    cooling_target_temperature: float
    hysteresis: float

    # Energy
    instantaneous_energy_surplus: float
    minimum_energy_surplus: float

    # Runtime State Snapshot
    current_heating_source: HeatingSource
    current_operation: CurrentOperation
    device_started_at: float
    demand_ended_at: float
    source_selected_at: float
    desired_source_differs_since: float

    # Device State Snapshot
    current_boiler_power_state: PowerState
    current_climate_power_state: PowerState
    current_climate_hvac_mode: ClimateHVACMode
    current_climate_target_temperature: float

    # Protection Configuration
    now: float
    minimum_runtime: float
    shutdown_delay: float
    source_change_delay: float
