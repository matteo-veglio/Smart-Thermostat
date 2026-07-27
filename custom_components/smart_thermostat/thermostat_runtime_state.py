from dataclasses import dataclass

from .source_engine import HeatingSource


@dataclass
class ThermostatRuntimeState:
    current_heating_source: HeatingSource = HeatingSource.BOILER
    device_started_at: float = 0.0
    demand_ended_at: float = 0.0
    source_selected_at: float = 0.0
    desired_source_differs_since: float = 0.0
