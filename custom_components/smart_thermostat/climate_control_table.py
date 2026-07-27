from dataclasses import dataclass

from .thermostat_runtime_state import CurrentOperation


@dataclass(frozen=True)
class ClimateControlTableEntry:
    minimum_temperature_error: float
    maximum_temperature_error: float
    requested_target_temperature: float


DEFAULT_HEATING_TABLE: tuple[ClimateControlTableEntry, ...] = (
    ClimateControlTableEntry(float("-inf"), 0.0, 20.0),
    ClimateControlTableEntry(0.0, 1.5, 22.0),
    ClimateControlTableEntry(1.5, 3.0, 25.0),
    ClimateControlTableEntry(3.0, float("inf"), 28.0),
)

DEFAULT_COOLING_TABLE: tuple[ClimateControlTableEntry, ...] = (
    ClimateControlTableEntry(float("-inf"), 0.0, 26.0),
    ClimateControlTableEntry(0.0, 1.5, 23.0),
    ClimateControlTableEntry(1.5, 3.0, 20.0),
    ClimateControlTableEntry(3.0, float("inf"), 18.0),
)


class ClimateControlTable:
    def __init__(
        self,
        heating_table: tuple[ClimateControlTableEntry, ...],
        cooling_table: tuple[ClimateControlTableEntry, ...],
    ) -> None:
        self._heating_table = heating_table
        self._cooling_table = cooling_table

    def resolve_target_temperature(
        self,
        *,
        requested_operation: CurrentOperation,
        current_temperature: float,
        heating_target_temperature: float,
        cooling_target_temperature: float,
    ) -> float:
        if requested_operation == CurrentOperation.HEATING:
            temperature_error = heating_target_temperature - current_temperature
            table = self._heating_table
        else:
            temperature_error = current_temperature - cooling_target_temperature
            table = self._cooling_table

        for entry in table:
            if entry.minimum_temperature_error <= temperature_error < entry.maximum_temperature_error:
                return entry.requested_target_temperature

        raise ValueError(f"No Climate Control Table entry matches temperature error {temperature_error}")
