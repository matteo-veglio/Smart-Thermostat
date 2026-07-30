from typing import Any

import voluptuous as vol
from homeassistant.components.climate import PRESET_AWAY, PRESET_HOME, PRESET_SLEEP
from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.const import CONF_NAME, STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import selector

from .const import DOMAIN

# specs/24_configuration_flow.md §4 Devices Step
CONF_CLIMATE_DEVICE = "climate_device"
CONF_BOILER = "boiler"

# specs/24_configuration_flow.md §5 Energy Step
CONF_INSTANTANEOUS_ENERGY_SURPLUS = "instantaneous_energy_surplus"
CONF_MINIMUM_ENERGY_SURPLUS = "minimum_energy_surplus"

# specs/24_configuration_flow.md §6 Protection Step
CONF_THERMOSTAT_TOLERANCE = "thermostat_tolerance"
CONF_SHUTDOWN_DELAY = "shutdown_delay"
CONF_SOURCE_CHANGE_DELAY = "source_change_delay"
CONF_MINIMUM_RUNTIME = "minimum_runtime"

# specs/27_climate_control_architecture.md §12 / specs/28_climate_control_mathematical_model.md §6
# Climate Regulation Step (Climate Control Algorithm configuration parameters)
CONF_KP = "kp"
CONF_TI = "ti"
CONF_TT = "tt"
CONF_TS = "ts"
CONF_TAC_MIN = "tac_min"
CONF_TAC_MAX = "tac_max"

# Control Diagnostics feature
CONF_ENABLE_CONTROL_DIAGNOSTICS = "enable_control_diagnostics"

# specs/24_configuration_flow.md §8-11 Preset Steps (generic field names, namespaced per Preset)
CONF_HEATING_TARGET = "heating_target"
CONF_COOLING_TARGET = "cooling_target"
CONF_TEMPERATURE_ENTITY = "temperature_entity"
CONF_HUMIDITY_ENTITY = "humidity_entity"

PRESETS: tuple[str, ...] = (PRESET_HOME, PRESET_AWAY, PRESET_SLEEP)


def preset_data_key(preset: str, field: str) -> str:
    return f"{preset}_{field}"


def _required(key: str) -> vol.Marker:
    return vol.Required(key)


def _optional(key: str) -> vol.Marker:
    return vol.Optional(key)


def general_schema() -> vol.Schema:
    return vol.Schema(
        {
            _required(CONF_NAME): selector.TextSelector(),
        }
    )


def devices_schema() -> vol.Schema:
    return vol.Schema(
        {
            _required(CONF_CLIMATE_DEVICE): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="climate")
            ),
            # specs/24_configuration_flow.md §4 Devices Step: the Boiler is mandatory,
            # exactly like the Climate Device - a searchable Entity Selector with no
            # default value and no placeholder option. Pre-filling the current value in
            # the Options Flow is handled via add_suggested_values_to_schema(), never via
            # a schema default - a default would make Home Assistant's frontend render
            # the field as "(optional)" even though it remains vol.Required.
            _required(CONF_BOILER): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="switch")
            ),
        }
    )


def energy_schema() -> vol.Schema:
    return vol.Schema(
        {
            _required(CONF_INSTANTANEOUS_ENERGY_SURPLUS): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor")
            ),
            _required(CONF_MINIMUM_ENERGY_SURPLUS): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=["number", "input_number"])
            ),
        }
    )


def protection_schema() -> vol.Schema:
    return vol.Schema(
        {
            _required(CONF_THERMOSTAT_TOLERANCE): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    mode=selector.NumberSelectorMode.BOX,
                    unit_of_measurement="°C",
                    step="any",
                )
            ),
            _required(CONF_SHUTDOWN_DELAY): selector.DurationSelector(),
            _required(CONF_SOURCE_CHANGE_DELAY): selector.DurationSelector(),
            _required(CONF_MINIMUM_RUNTIME): selector.DurationSelector(),
        }
    )


def climate_regulation_schema() -> vol.Schema:
    return vol.Schema(
        {
            _required(CONF_KP): selector.NumberSelector(
                selector.NumberSelectorConfig(mode=selector.NumberSelectorMode.BOX, step="any")
            ),
            _required(CONF_TI): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    mode=selector.NumberSelectorMode.BOX, unit_of_measurement="s", step="any"
                )
            ),
            _required(CONF_TT): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    mode=selector.NumberSelectorMode.BOX, unit_of_measurement="s", step="any"
                )
            ),
            _required(CONF_TS): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    mode=selector.NumberSelectorMode.BOX, unit_of_measurement="s", step="any"
                )
            ),
            _required(CONF_TAC_MIN): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    mode=selector.NumberSelectorMode.BOX, unit_of_measurement="°C", step="any"
                )
            ),
            _required(CONF_TAC_MAX): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    mode=selector.NumberSelectorMode.BOX, unit_of_measurement="°C", step="any"
                )
            ),
            # Control Diagnostics: default=False is a genuine fallback value (what a
            # brand-new Config Entry should start with), not a prefill mechanism - it is
            # intentionally combined with add_suggested_values_to_schema() in the Options
            # Flow, which is the documented "mix and match" pattern: suggested_value
            # shows the current stored value, default is only used if the field were
            # ever left empty.
            vol.Required(CONF_ENABLE_CONTROL_DIAGNOSTICS, default=False): selector.BooleanSelector(),
        }
    )


def preset_schema() -> vol.Schema:
    return vol.Schema(
        {
            _required(CONF_HEATING_TARGET): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    mode=selector.NumberSelectorMode.BOX,
                    unit_of_measurement="°C",
                    step="any",
                )
            ),
            _required(CONF_COOLING_TARGET): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    mode=selector.NumberSelectorMode.BOX,
                    unit_of_measurement="°C",
                    step="any",
                )
            ),
            _required(CONF_TEMPERATURE_ENTITY): selector.EntitySelector(),
            _optional(CONF_HUMIDITY_ENTITY): selector.EntitySelector(),
        }
    )


def _entity_exposes_numeric_value(hass: HomeAssistant, entity_id: str) -> bool:
    state = hass.states.get(entity_id)

    if state is None or state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
        return False

    try:
        float(state.state)
    except ValueError:
        return False

    return True


def validate_devices(hass: HomeAssistant, user_input: dict[str, Any]) -> dict[str, str]:
    errors: dict[str, str] = {}

    if hass.states.get(user_input[CONF_CLIMATE_DEVICE]) is None:
        errors[CONF_CLIMATE_DEVICE] = "entity_not_found"

    if hass.states.get(user_input[CONF_BOILER]) is None:
        errors[CONF_BOILER] = "entity_not_found"

    return errors


def validate_energy(hass: HomeAssistant, user_input: dict[str, Any]) -> dict[str, str]:
    errors: dict[str, str] = {}

    if not _entity_exposes_numeric_value(hass, user_input[CONF_INSTANTANEOUS_ENERGY_SURPLUS]):
        errors[CONF_INSTANTANEOUS_ENERGY_SURPLUS] = "invalid_numeric_entity"

    if not _entity_exposes_numeric_value(hass, user_input[CONF_MINIMUM_ENERGY_SURPLUS]):
        errors[CONF_MINIMUM_ENERGY_SURPLUS] = "invalid_numeric_entity"

    return errors


def validate_preset(hass: HomeAssistant, user_input: dict[str, Any]) -> dict[str, str]:
    errors: dict[str, str] = {}

    if not _entity_exposes_numeric_value(hass, user_input[CONF_TEMPERATURE_ENTITY]):
        errors[CONF_TEMPERATURE_ENTITY] = "invalid_numeric_entity"

    humidity_entity_id = user_input.get(CONF_HUMIDITY_ENTITY)

    if humidity_entity_id is not None and not _entity_exposes_numeric_value(hass, humidity_entity_id):
        errors[CONF_HUMIDITY_ENTITY] = "invalid_numeric_entity"

    return errors


def preset_defaults(data: dict[str, Any], preset: str) -> dict[str, Any]:
    """Extract the generic (non-namespaced) defaults for one Preset out of stored Config Entry data."""
    defaults: dict[str, Any] = {}

    for field in (CONF_HEATING_TARGET, CONF_COOLING_TARGET, CONF_TEMPERATURE_ENTITY, CONF_HUMIDITY_ENTITY):
        key = preset_data_key(preset, field)

        if key in data:
            defaults[field] = data[key]

    return defaults


def store_preset_fields(data: dict[str, Any], preset: str, user_input: dict[str, Any]) -> None:
    for field in (CONF_HEATING_TARGET, CONF_COOLING_TARGET, CONF_TEMPERATURE_ENTITY, CONF_HUMIDITY_ENTITY):
        if field in user_input:
            data[preset_data_key(preset, field)] = user_input[field]


class SmartThermostatConfigFlow(ConfigFlow, domain=DOMAIN):
    # Version 3: the custom "night" Preset identifier was replaced by the standard Home
    # Assistant "sleep" Preset.
    # Version 4: the Boiler became a mandatory field with an explicit "No Boiler" value.
    # Version 5: the "No Boiler" value was removed - the Boiler is now a strictly
    # mandatory real entity, exactly like the Climate Device, with no placeholder.
    # Version 6: Minimum Device Runtime and Minimum Source Runtime were consolidated
    # into a single Minimum Runtime parameter, applied both before stopping the active
    # device and before replacing it with a different heating source.
    # See __init__.py async_migrate_entry.
    VERSION = 6

    def __init__(self) -> None:
        self._data: dict[str, Any] = {}

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        from .options_flow import SmartThermostatOptionsFlow

        return SmartThermostatOptionsFlow()

    # specs/24_configuration_flow.md §3 General Step
    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> dict:
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_devices()

        return self.async_show_form(step_id="user", data_schema=general_schema())

    # specs/24_configuration_flow.md §4 Devices Step
    async def async_step_devices(self, user_input: dict[str, Any] | None = None) -> dict:
        errors: dict[str, str] = {}

        if user_input is not None:
            errors = validate_devices(self.hass, user_input)

            if not errors:
                self._data.update(user_input)
                return await self.async_step_energy()

        return self.async_show_form(step_id="devices", data_schema=devices_schema(), errors=errors)

    # specs/24_configuration_flow.md §5 Energy Step
    async def async_step_energy(self, user_input: dict[str, Any] | None = None) -> dict:
        errors: dict[str, str] = {}

        if user_input is not None:
            errors = validate_energy(self.hass, user_input)

            if not errors:
                self._data.update(user_input)
                return await self.async_step_protection()

        return self.async_show_form(step_id="energy", data_schema=energy_schema(), errors=errors)

    # specs/24_configuration_flow.md §6 Protection Step
    async def async_step_protection(self, user_input: dict[str, Any] | None = None) -> dict:
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_climate_regulation()

        return self.async_show_form(step_id="protection", data_schema=protection_schema())

    # specs/27_climate_control_architecture.md §12 Configuration
    async def async_step_climate_regulation(self, user_input: dict[str, Any] | None = None) -> dict:
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_preset_home()

        return self.async_show_form(step_id="climate_regulation", data_schema=climate_regulation_schema())

    # specs/24_configuration_flow.md §7 Preset Steps
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
            errors = validate_preset(self.hass, user_input)

            if not errors:
                store_preset_fields(self._data, preset, user_input)
                return await next_step()

        return self.async_show_form(step_id=step_id, data_schema=preset_schema(), errors=errors)

    async def _async_finish(self) -> dict:
        return self.async_create_entry(title=self._data[CONF_NAME], data=self._data)
