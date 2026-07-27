from homeassistant.config_entries import ConfigFlow

from .const import DOMAIN


class SmartThermostatConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None) -> dict:
        if user_input is not None:
            return self.async_create_entry(title="Smart Thermostat", data={})

        return self.async_show_form(step_id="user")
