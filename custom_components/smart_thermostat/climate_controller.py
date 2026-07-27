from homeassistant.components.climate import (
    ATTR_HVAC_MODE,
    SERVICE_SET_HVAC_MODE,
    SERVICE_SET_TEMPERATURE,
    HVACMode,
)
from homeassistant.const import ATTR_ENTITY_ID, ATTR_TEMPERATURE, SERVICE_TURN_OFF, SERVICE_TURN_ON, Platform
from homeassistant.core import HomeAssistant


class ClimateController:
    def __init__(self, hass: HomeAssistant, entity_id: str) -> None:
        self._hass = hass
        self._entity_id = entity_id

    async def turn_on(self) -> None:
        await self._hass.services.async_call(
            Platform.CLIMATE,
            SERVICE_TURN_ON,
            {ATTR_ENTITY_ID: self._entity_id},
            blocking=True,
        )

    async def turn_off(self) -> None:
        await self._hass.services.async_call(
            Platform.CLIMATE,
            SERVICE_TURN_OFF,
            {ATTR_ENTITY_ID: self._entity_id},
            blocking=True,
        )

    async def set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        await self._hass.services.async_call(
            Platform.CLIMATE,
            SERVICE_SET_HVAC_MODE,
            {ATTR_ENTITY_ID: self._entity_id, ATTR_HVAC_MODE: hvac_mode},
            blocking=True,
        )

    async def set_target_temperature(self, temperature: float) -> None:
        await self._hass.services.async_call(
            Platform.CLIMATE,
            SERVICE_SET_TEMPERATURE,
            {ATTR_ENTITY_ID: self._entity_id, ATTR_TEMPERATURE: temperature},
            blocking=True,
        )
