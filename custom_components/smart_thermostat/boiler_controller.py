from homeassistant.const import ATTR_ENTITY_ID, SERVICE_TURN_OFF, SERVICE_TURN_ON, Platform
from homeassistant.core import HomeAssistant


class BoilerController:
    def __init__(self, hass: HomeAssistant, entity_id: str) -> None:
        self._hass = hass
        self._entity_id = entity_id

    async def turn_on(self) -> None:
        await self._hass.services.async_call(
            Platform.SWITCH,
            SERVICE_TURN_ON,
            {ATTR_ENTITY_ID: self._entity_id},
            blocking=True,
        )

    async def turn_off(self) -> None:
        await self._hass.services.async_call(
            Platform.SWITCH,
            SERVICE_TURN_OFF,
            {ATTR_ENTITY_ID: self._entity_id},
            blocking=True,
        )
