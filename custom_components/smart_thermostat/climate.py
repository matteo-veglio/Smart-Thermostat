from typing import Any

from homeassistant.components.climate import (
    ATTR_TARGET_TEMP_HIGH,
    ATTR_TARGET_TEMP_LOW,
    PRESET_AWAY,
    PRESET_HOME,
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)

PRESET_NIGHT = "night"


class SmartThermostatClimateEntity(ClimateEntity):
    # General
    _attr_name: str | None = None
    _attr_unique_id: str | None = None
    _attr_available: bool = True

    # Temperature
    _attr_current_temperature: float | None = None
    _attr_current_humidity: float | None = None
    _attr_target_temperature_high: float | None = None
    _attr_target_temperature_low: float | None = None

    # HVAC
    _attr_hvac_mode: HVACMode | None = None
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT_COOL]
    _attr_hvac_action: HVACAction | None = None

    # Presets
    _attr_preset_mode: str | None = None
    _attr_preset_modes = [PRESET_AWAY, PRESET_HOME, PRESET_NIGHT]

    # Supported Features
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE_RANGE
        | ClimateEntityFeature.PRESET_MODE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
    )

    @property
    def temperature_unit(self) -> str:
        return self.hass.config.units.temperature_unit

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        self._attr_hvac_mode = hvac_mode
        self.async_write_ha_state()

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        self._attr_preset_mode = preset_mode
        self.async_write_ha_state()

    async def async_set_temperature(self, **kwargs: Any) -> None:
        if ATTR_TARGET_TEMP_HIGH in kwargs:
            self._attr_target_temperature_high = kwargs[ATTR_TARGET_TEMP_HIGH]

        if ATTR_TARGET_TEMP_LOW in kwargs:
            self._attr_target_temperature_low = kwargs[ATTR_TARGET_TEMP_LOW]

        self.async_write_ha_state()
