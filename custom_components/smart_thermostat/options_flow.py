from typing import Any

from homeassistant.components.climate import PRESET_AWAY, PRESET_HOME, PRESET_SLEEP
from homeassistant.config_entries import OptionsFlow
from homeassistant.const import CONF_NAME

from . import config_flow as cf


class SmartThermostatOptionsFlow(OptionsFlow):
    """specs/25_options_flow.md

    Exposes exactly the same configuration as SmartThermostatConfigFlow, reusing its
    schema-building and validation functions so both flows are always functionally
    equivalent (specs/25_options_flow.md §2, §6).
    """

    def __init__(self) -> None:
        self._data: dict[str, Any] = {}

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> dict:
        self._data = dict(self.config_entry.data)
        return await self.async_step_general()

    async def async_step_general(self, user_input: dict[str, Any] | None = None) -> dict:
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_devices()

        return self.async_show_form(
            step_id="general",
            data_schema=self.add_suggested_values_to_schema(cf.general_schema(), self._data),
        )

    async def async_step_devices(self, user_input: dict[str, Any] | None = None) -> dict:
        errors: dict[str, str] = {}

        if user_input is not None:
            errors = cf.validate_devices(self.hass, user_input)

            if not errors:
                self._data.update(user_input)
                return await self.async_step_energy()

        return self.async_show_form(
            step_id="devices",
            data_schema=self.add_suggested_values_to_schema(cf.devices_schema(), self._data),
            errors=errors,
        )

    async def async_step_energy(self, user_input: dict[str, Any] | None = None) -> dict:
        errors: dict[str, str] = {}

        if user_input is not None:
            errors = cf.validate_energy(self.hass, user_input)

            if not errors:
                self._data.update(user_input)
                return await self.async_step_protection()

        return self.async_show_form(
            step_id="energy",
            data_schema=self.add_suggested_values_to_schema(cf.energy_schema(), self._data),
            errors=errors,
        )

    async def async_step_protection(self, user_input: dict[str, Any] | None = None) -> dict:
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_climate_regulation()

        return self.async_show_form(
            step_id="protection",
            data_schema=self.add_suggested_values_to_schema(cf.protection_schema(), self._data),
        )

    async def async_step_climate_regulation(self, user_input: dict[str, Any] | None = None) -> dict:
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_preset_home()

        return self.async_show_form(
            step_id="climate_regulation",
            data_schema=self.add_suggested_values_to_schema(cf.climate_regulation_schema(), self._data),
        )

    async def async_step_preset_home(self, user_input: dict[str, Any] | None = None) -> dict:
        return await self._async_step_preset(PRESET_HOME, "preset_home", user_input, self.async_step_preset_away)

    async def async_step_preset_away(self, user_input: dict[str, Any] | None = None) -> dict:
        return await self._async_step_preset(PRESET_AWAY, "preset_away", user_input, self.async_step_preset_sleep)

    async def async_step_preset_sleep(self, user_input: dict[str, Any] | None = None) -> dict:
        return await self._async_step_preset(PRESET_SLEEP, "preset_sleep", user_input, self._async_finish)

    async def _async_step_preset(
        self,
        preset: str,
        step_id: str,
        user_input: dict[str, Any] | None,
        next_step,
    ) -> dict:
        errors: dict[str, str] = {}

        if user_input is not None:
            errors = cf.validate_preset(self.hass, user_input)

            if not errors:
                cf.store_preset_fields(self._data, preset, user_input)
                return await next_step()

        defaults = cf.preset_defaults(self._data, preset)
        return self.async_show_form(
            step_id=step_id,
            data_schema=self.add_suggested_values_to_schema(cf.preset_schema(), defaults),
            errors=errors,
        )

    async def _async_finish(self) -> dict:
        # specs/25_options_flow.md §3 Configuration Update / §4 Runtime Behaviour
        # Only user configuration is updated here; the standard Home Assistant Config
        # Entry update listener (registered in __init__.py) triggers the reload.
        self.hass.config_entries.async_update_entry(
            self.config_entry,
            data=self._data,
            title=self._data[CONF_NAME],
        )
        return self.async_create_entry(title="", data={})
