from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import HomeAssistant

from .device_action import ClimateHVACMode, PowerState
from .preset_configuration import PresetConfiguration
from .runtime_context import RuntimeContext
from .state_machine import ThermostatState
from .target_mode import TargetMode
from .thermostat_runtime_state import ThermostatRuntimeState


class RuntimeContextFactory:
    def __init__(
        self,
        hass: HomeAssistant,
        runtime_state: ThermostatRuntimeState,
        presets: dict[str, PresetConfiguration],
    ) -> None:
        self._hass = hass
        self._runtime_state = runtime_state
        self._presets = presets

    @property
    def entity_ids_to_track(self) -> frozenset[str]:
        entity_ids: set[str] = set()

        for preset in self._presets.values():
            entity_ids.add(preset.temperature_entity_id)

            if preset.humidity_entity_id is not None:
                entity_ids.add(preset.humidity_entity_id)

        return frozenset(entity_ids)

    def create(
        self,
        *,
        active_preset: str,
        target_mode: TargetMode,
        current_state: ThermostatState,
        hysteresis: float,
        instantaneous_energy_surplus: float,
        minimum_energy_surplus: float,
        now: float,
        minimum_runtime: float,
        shutdown_delay: float,
        source_change_delay: float,
        manual_heating_target_temperature: float | None = None,
        manual_cooling_target_temperature: float | None = None,
        current_boiler_power_state: PowerState = PowerState.OFF,
        current_climate_power_state: PowerState = PowerState.OFF,
        current_climate_hvac_mode: ClimateHVACMode = ClimateHVACMode.HEAT,
        current_climate_target_temperature: float = 0.0,
    ) -> RuntimeContext | None:
        # specs/23_preset_configuration.md §4 Runtime Context
        preset = self._presets[active_preset]

        # specs/26_target_mode.md §10/§11: this is the single point resolving which
        # source of target temperatures is currently active. Sensor entities (current
        # temperature/humidity) always come from the active Preset regardless of Target
        # Mode - only the numeric Heating/Cooling Target depend on it.
        if target_mode == TargetMode.MANUAL:
            heating_target_temperature = manual_heating_target_temperature
            cooling_target_temperature = manual_cooling_target_temperature
        else:
            heating_target_temperature = preset.heating_target_temperature
            cooling_target_temperature = preset.cooling_target_temperature

        current_temperature = self._read_required_value(preset.temperature_entity_id)

        if current_temperature is None:
            return None

        current_humidity = self._read_optional_value(preset.humidity_entity_id)

        return RuntimeContext(
            current_state=current_state,
            current_temperature=current_temperature,
            current_humidity=current_humidity,
            heating_target_temperature=heating_target_temperature,
            cooling_target_temperature=cooling_target_temperature,
            hysteresis=hysteresis,
            instantaneous_energy_surplus=instantaneous_energy_surplus,
            minimum_energy_surplus=minimum_energy_surplus,
            current_heating_source=self._runtime_state.current_heating_source,
            current_operation=self._runtime_state.current_operation,
            device_started_at=self._runtime_state.device_started_at,
            demand_ended_at=self._runtime_state.demand_ended_at,
            source_selected_at=self._runtime_state.source_selected_at,
            desired_source_differs_since=self._runtime_state.desired_source_differs_since,
            current_boiler_power_state=current_boiler_power_state,
            current_climate_power_state=current_climate_power_state,
            current_climate_hvac_mode=current_climate_hvac_mode,
            current_climate_target_temperature=current_climate_target_temperature,
            now=now,
            minimum_runtime=minimum_runtime,
            shutdown_delay=shutdown_delay,
            source_change_delay=source_change_delay,
        )

    def _read_required_value(self, entity_id: str) -> float | None:
        state = self._hass.states.get(entity_id)

        if state is None or state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            return None

        try:
            return float(state.state)
        except ValueError:
            return None

    def _read_optional_value(self, entity_id: str | None) -> float | None:
        if entity_id is None:
            return None

        return self._read_required_value(entity_id)
