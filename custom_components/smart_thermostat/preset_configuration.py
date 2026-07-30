from dataclasses import dataclass


@dataclass(frozen=True)
class PresetConfiguration:
    """specs/23_preset_configuration.md §3 Preset Configuration"""

    heating_target_temperature: float
    cooling_target_temperature: float
    temperature_entity_id: str
    humidity_entity_id: str | None
