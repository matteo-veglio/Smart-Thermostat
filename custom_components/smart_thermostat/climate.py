import time
from datetime import timedelta
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
from homeassistant.const import CONF_NAME, PRECISION_TENTHS, PRECISION_WHOLE, STATE_UNAVAILABLE, STATE_UNKNOWN, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .boiler_controller import BoilerController
from .climate_controller import ClimateController
from .config_flow import (
    CONF_INDOOR_HUMIDITY_SENSOR,
    CONF_INDOOR_TEMPERATURE_SENSOR,
    CONF_INSTANTANEOUS_ENERGY_SURPLUS,
    CONF_MINIMUM_DEVICE_RUNTIME,
    CONF_MINIMUM_ENERGY_SURPLUS,
    CONF_MINIMUM_SOURCE_RUNTIME,
    CONF_SHUTDOWN_DELAY,
    CONF_SOURCE_CHANGE_DELAY,
    CONF_THERMOSTAT_TOLERANCE,
)
from .device_action import (
    ClimateHVACMode,
    DeviceAction,
    SetClimateHVACMode,
    SetClimateTargetTemperature,
    TurnBoilerOff,
    TurnBoilerOn,
    TurnClimateOff,
    TurnClimateOn,
)
from .runtime_context_factory import RuntimeContextFactory
from .runtime_data import SmartThermostatConfigEntry
from .state_machine import StateMachine, ThermostatState
from .thermostat_controller import ThermostatController, ThermostatControllerResult
from .thermostat_runtime_state import CurrentOperation

PRESET_NIGHT = "night"

_HVAC_ACTION_MAP: dict[tuple[ThermostatState, CurrentOperation], HVACAction] = {
    (ThermostatState.OFF, CurrentOperation.NONE): HVACAction.OFF,
    (ThermostatState.IDLE, CurrentOperation.NONE): HVACAction.IDLE,
    (ThermostatState.STARTING, CurrentOperation.HEATING): HVACAction.HEATING,
    (ThermostatState.STARTING, CurrentOperation.COOLING): HVACAction.COOLING,
    (ThermostatState.HEATING, CurrentOperation.HEATING): HVACAction.HEATING,
    (ThermostatState.COOLING, CurrentOperation.COOLING): HVACAction.COOLING,
    (ThermostatState.STOPPING, CurrentOperation.HEATING): HVACAction.HEATING,
    (ThermostatState.STOPPING, CurrentOperation.COOLING): HVACAction.COOLING,
}

_CLIMATE_HVAC_MODE_MAP: dict[ClimateHVACMode, HVACMode] = {
    ClimateHVACMode.HEAT: HVACMode.HEAT,
    ClimateHVACMode.COOL: HVACMode.COOL,
}


def _duration_to_seconds(duration: dict[str, float]) -> float:
    return timedelta(**duration).total_seconds()


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SmartThermostatConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities(
        [
            SmartThermostatClimateEntity(
                thermostat_controller=entry.runtime_data.thermostat_controller,
                runtime_context_factory=entry.runtime_data.runtime_context_factory,
                state_machine=entry.runtime_data.state_machine,
                boiler_controller=entry.runtime_data.boiler_controller,
                heating_climate_controller=entry.runtime_data.heating_climate_controller,
                cooling_climate_controller=entry.runtime_data.cooling_climate_controller,
                unique_id=entry.entry_id,
                name=entry.data[CONF_NAME],
                indoor_temperature_sensor_entity_id=entry.data[CONF_INDOOR_TEMPERATURE_SENSOR],
                indoor_humidity_sensor_entity_id=entry.data.get(CONF_INDOOR_HUMIDITY_SENSOR),
                instantaneous_energy_surplus_entity_id=entry.data[CONF_INSTANTANEOUS_ENERGY_SURPLUS],
                minimum_energy_surplus_entity_id=entry.data[CONF_MINIMUM_ENERGY_SURPLUS],
                hysteresis=entry.data[CONF_THERMOSTAT_TOLERANCE],
                minimum_device_runtime=_duration_to_seconds(entry.data[CONF_MINIMUM_DEVICE_RUNTIME]),
                minimum_source_runtime=_duration_to_seconds(entry.data[CONF_MINIMUM_SOURCE_RUNTIME]),
                shutdown_delay=_duration_to_seconds(entry.data[CONF_SHUTDOWN_DELAY]),
                source_change_delay=_duration_to_seconds(entry.data[CONF_SOURCE_CHANGE_DELAY]),
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
        runtime_context_factory: RuntimeContextFactory,
        state_machine: StateMachine,
        boiler_controller: BoilerController,
        heating_climate_controller: ClimateController,
        cooling_climate_controller: ClimateController,
        unique_id: str,
        name: str,
        indoor_temperature_sensor_entity_id: str,
        indoor_humidity_sensor_entity_id: str | None,
        instantaneous_energy_surplus_entity_id: str,
        minimum_energy_surplus_entity_id: str,
        hysteresis: float,
        minimum_device_runtime: float,
        minimum_source_runtime: float,
        shutdown_delay: float,
        source_change_delay: float,
    ) -> None:
        self._thermostat_controller = thermostat_controller
        self._runtime_context_factory = runtime_context_factory
        self._state_machine = state_machine
        self._boiler_controller = boiler_controller
        self._heating_climate_controller = heating_climate_controller
        self._cooling_climate_controller = cooling_climate_controller

        self._indoor_temperature_sensor_entity_id = indoor_temperature_sensor_entity_id
        self._indoor_humidity_sensor_entity_id = indoor_humidity_sensor_entity_id
        self._instantaneous_energy_surplus_entity_id = instantaneous_energy_surplus_entity_id
        self._minimum_energy_surplus_entity_id = minimum_energy_surplus_entity_id
        self._hysteresis = hysteresis
        self._minimum_device_runtime = minimum_device_runtime
        self._minimum_source_runtime = minimum_source_runtime
        self._shutdown_delay = shutdown_delay
        self._source_change_delay = source_change_delay

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

    def _read_required_value(self, entity_id: str) -> float | None:
        state = self.hass.states.get(entity_id)

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

    async def async_evaluate(self) -> None:
        current_temperature = self._read_required_value(self._indoor_temperature_sensor_entity_id)
        instantaneous_energy_surplus = self._read_required_value(self._instantaneous_energy_surplus_entity_id)
        minimum_energy_surplus = self._read_required_value(self._minimum_energy_surplus_entity_id)
        heating_target_temperature = self._attr_target_temperature_low
        cooling_target_temperature = self._attr_target_temperature_high

        if (
            current_temperature is None
            or instantaneous_energy_surplus is None
            or minimum_energy_surplus is None
            or heating_target_temperature is None
            or cooling_target_temperature is None
        ):
            self._attr_available = False
            self.async_write_ha_state()
            return

        current_humidity = self._read_optional_value(self._indoor_humidity_sensor_entity_id)

        context = self._runtime_context_factory.create(
            current_state=self._state_machine.current_state,
            current_temperature=current_temperature,
            current_humidity=current_humidity,
            heating_target_temperature=heating_target_temperature,
            cooling_target_temperature=cooling_target_temperature,
            hysteresis=self._hysteresis,
            instantaneous_energy_surplus=instantaneous_energy_surplus,
            minimum_energy_surplus=minimum_energy_surplus,
            now=time.monotonic(),
            minimum_device_runtime=self._minimum_device_runtime,
            minimum_source_runtime=self._minimum_source_runtime,
            shutdown_delay=self._shutdown_delay,
            source_change_delay=self._source_change_delay,
        )

        result = self._thermostat_controller.evaluate(context)

        self._attr_available = True
        self._attr_current_temperature = current_temperature
        self._attr_current_humidity = current_humidity
        self._attr_hvac_action = _HVAC_ACTION_MAP[(result.current_state, result.current_operation)]

        self.async_write_ha_state()

        await self._async_execute_requested_device_actions(result)

    def _select_climate_controller(self, requested_operation: CurrentOperation) -> ClimateController:
        if requested_operation == CurrentOperation.COOLING:
            return self._cooling_climate_controller

        return self._heating_climate_controller

    async def _async_execute_requested_device_actions(self, result: ThermostatControllerResult) -> None:
        climate_controller = self._select_climate_controller(result.requested_operation)

        for action in result.requested_device_actions:
            await self._async_execute_device_action(action, climate_controller)

    async def _async_execute_device_action(
        self,
        action: DeviceAction,
        climate_controller: ClimateController,
    ) -> None:
        if isinstance(action, TurnBoilerOn):
            await self._boiler_controller.turn_on()
        elif isinstance(action, TurnBoilerOff):
            await self._boiler_controller.turn_off()
        elif isinstance(action, TurnClimateOn):
            await climate_controller.turn_on()
        elif isinstance(action, TurnClimateOff):
            await climate_controller.turn_off()
        elif isinstance(action, SetClimateHVACMode):
            await climate_controller.set_hvac_mode(_CLIMATE_HVAC_MODE_MAP[action.hvac_mode])
        elif isinstance(action, SetClimateTargetTemperature):
            await climate_controller.set_target_temperature(action.target_temperature)
