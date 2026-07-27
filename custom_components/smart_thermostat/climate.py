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
from homeassistant.const import CONF_NAME, PRECISION_TENTHS, PRECISION_WHOLE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .runtime_data import SmartThermostatConfigEntry
from .thermostat_controller import ThermostatController

PRESET_NIGHT = "night"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SmartThermostatConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities(
        [
            SmartThermostatClimateEntity(
                thermostat_controller=entry.runtime_data.thermostat_controller,
                unique_id=entry.entry_id,
                name=entry.data[CONF_NAME],
            )
        ]
    )


class SmartThermostatClimateEntity(ClimateEntity):
    # HVAC
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT_COOL]

    # Presets
    _attr_preset_modes = [PRESET_AWAY, PRESET_HOME, PRESET_NIGHT]

    # Supported Features
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE_RANGE
        | ClimateEntityFeature.PRESET_MODE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
    )

    def __init__(
        self,
        thermostat_controller: ThermostatController,
        unique_id: str,
        name: str,
    ) -> None:
        self._thermostat_controller = thermostat_controller

        # General
        self._attr_name: str | None = name
        self._attr_unique_id: str | None = unique_id
        self._attr_available: bool = True

        # Temperature
        self._attr_current_temperature: float | None = None
        self._attr_current_humidity: float | None = None
        self._attr_target_temperature_high: float | None = None
        self._attr_target_temperature_low: float | None = None

        # HVAC
        self._attr_hvac_mode: HVACMode | None = None
        self._attr_hvac_action: HVACAction | None = None

        # Presets
        self._attr_preset_mode: str | None = None

    @property
    def temperature_unit(self) -> str:
        return self.hass.config.units.temperature_unit

    @property
    def precision(self) -> float:
        if self.temperature_unit == UnitOfTemperature.CELSIUS:
            return PRECISION_TENTHS
        return PRECISION_WHOLE

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        self._attr_hvac_mode = hvac_mode
        self.async_write_ha_state()

    async def async_turn_on(self) -> None:
        await self.async_set_hvac_mode(HVACMode.HEAT_COOL)

    async def async_turn_off(self) -> None:
        await self.async_set_hvac_mode(HVACMode.OFF)

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        self._attr_preset_mode = preset_mode
        self.async_write_ha_state()

    async def async_set_temperature(self, **kwargs: Any) -> None:
        if ATTR_TARGET_TEMP_HIGH in kwargs:
            self._attr_target_temperature_high = kwargs[ATTR_TARGET_TEMP_HIGH]

        if ATTR_TARGET_TEMP_LOW in kwargs:
            self._attr_target_temperature_low = kwargs[ATTR_TARGET_TEMP_LOW]

        self.async_write_ha_state()
