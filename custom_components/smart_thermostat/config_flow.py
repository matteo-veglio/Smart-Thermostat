import voluptuous as vol
from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_NAME
from homeassistant.helpers import selector

from .const import DOMAIN

CONF_INDOOR_TEMPERATURE_SENSOR = "indoor_temperature_sensor"
CONF_INDOOR_HUMIDITY_SENSOR = "indoor_humidity_sensor"
CONF_HEATING_SOURCE_1 = "heating_source_1"
CONF_HEATING_SOURCE_2 = "heating_source_2"
CONF_COOLING_SOURCE = "cooling_source"
CONF_INSTANTANEOUS_ENERGY_SURPLUS = "instantaneous_energy_surplus"
CONF_MINIMUM_ENERGY_SURPLUS = "minimum_energy_surplus"
CONF_THERMOSTAT_TOLERANCE = "thermostat_tolerance"
CONF_SHUTDOWN_DELAY = "shutdown_delay"
CONF_SOURCE_CHANGE_DELAY = "source_change_delay"
CONF_MINIMUM_DEVICE_RUNTIME = "minimum_device_runtime"
CONF_MINIMUM_SOURCE_RUNTIME = "minimum_source_runtime"

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): selector.TextSelector(),
        vol.Required(CONF_INDOOR_TEMPERATURE_SENSOR): selector.EntitySelector(
            selector.EntitySelectorConfig(domain="sensor")
        ),
        vol.Optional(CONF_INDOOR_HUMIDITY_SENSOR): selector.EntitySelector(
            selector.EntitySelectorConfig(domain="sensor")
        ),
        vol.Required(CONF_HEATING_SOURCE_1): selector.EntitySelector(
            selector.EntitySelectorConfig(domain="switch")
        ),
        vol.Required(CONF_HEATING_SOURCE_2): selector.EntitySelector(
            selector.EntitySelectorConfig(domain="climate")
        ),
        vol.Required(CONF_COOLING_SOURCE): selector.EntitySelector(
            selector.EntitySelectorConfig(domain="climate")
        ),
        vol.Required(CONF_INSTANTANEOUS_ENERGY_SURPLUS): selector.EntitySelector(
            selector.EntitySelectorConfig(domain="sensor")
        ),
        vol.Required(CONF_MINIMUM_ENERGY_SURPLUS): selector.EntitySelector(
            selector.EntitySelectorConfig(domain=["number","input_number",])
        ),
        vol.Required(CONF_THERMOSTAT_TOLERANCE): selector.NumberSelector(
            selector.NumberSelectorConfig(
                mode=selector.NumberSelectorMode.BOX,
                unit_of_measurement="°C",
                step="any",
            )
        ),
        vol.Required(CONF_SHUTDOWN_DELAY): selector.DurationSelector(),
        vol.Required(CONF_SOURCE_CHANGE_DELAY): selector.DurationSelector(),
        vol.Required(CONF_MINIMUM_DEVICE_RUNTIME): selector.DurationSelector(),
        vol.Required(CONF_MINIMUM_SOURCE_RUNTIME): selector.DurationSelector(),
    }
)


class SmartThermostatConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None) -> dict:
        if user_input is not None:
            return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

        return self.async_show_form(step_id="user", data_schema=STEP_USER_DATA_SCHEMA)
