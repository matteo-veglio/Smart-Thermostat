from homeassistant.components.climate import PRESET_SLEEP
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .boiler_controller import BoilerController
from .climate_control_algorithm import (
    ClimateControlAlgorithm,
    ClimateControlAlgorithmConfiguration,
    ClimateControlAlgorithmState,
)
from .climate_controller import ClimateController
from .config_flow import (
    CONF_BOILER,
    CONF_CLIMATE_DEVICE,
    CONF_COOLING_TARGET,
    CONF_ENABLE_CONTROL_DIAGNOSTICS,
    CONF_HEATING_TARGET,
    CONF_HUMIDITY_ENTITY,
    CONF_KP,
    CONF_MINIMUM_ENERGY_SURPLUS,
    CONF_MINIMUM_RUNTIME,
    CONF_SHUTDOWN_DELAY,
    CONF_SOURCE_CHANGE_DELAY,
    CONF_TAC_MAX,
    CONF_TAC_MIN,
    CONF_TEMPERATURE_ENTITY,
    CONF_THERMOSTAT_TOLERANCE,
    CONF_TI,
    CONF_TS,
    CONF_TT,
    PRESETS,
    preset_data_key,
)
from .const import LEGACY_PRESET_NIGHT
from .demand_engine import DemandEngine
from .preset_configuration import PresetConfiguration
from .protection_engine import ProtectionEngine
from .runtime_context_factory import RuntimeContextFactory
from .runtime_data import SmartThermostatConfigEntry, SmartThermostatRuntimeData
from .source_engine import SourceEngine
from .state_machine import StateMachine, ThermostatState
from .thermostat_controller import ThermostatController
from .thermostat_runtime_state import ThermostatRuntimeState
from .transition_table import TransitionTable

PLATFORMS: list[Platform] = [Platform.CLIMATE, Platform.SENSOR]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    return True


async def async_migrate_entry(hass: HomeAssistant, entry: SmartThermostatConfigEntry) -> bool:
    """Migrate a Config Entry created by an earlier version of the Smart Thermostat.

    Existing installations are migrated automatically; no user intervention is required
    and no configuration is lost.
    """
    version = entry.version
    data = dict(entry.data)

    if version < 3:
        # The custom "night" Preset identifier was replaced by the standard Home
        # Assistant "sleep" Preset - only the stored key prefix changes.
        for field in (CONF_HEATING_TARGET, CONF_COOLING_TARGET, CONF_TEMPERATURE_ENTITY, CONF_HUMIDITY_ENTITY):
            legacy_key = preset_data_key(LEGACY_PRESET_NIGHT, field)

            if legacy_key in data:
                data[preset_data_key(PRESET_SLEEP, field)] = data.pop(legacy_key)

        version = 3

    if version < 5:
        # The Boiler's explicit "No Boiler" placeholder value was removed - the Boiler
        # is now a strictly mandatory real entity, exactly like the Climate Device.
        # Entries still storing the placeholder (or never configured with a Boiler at
        # all) cannot be automatically migrated to a real entity - a configuration
        # without a Boiler is invalid by definition - and must be reconfigured through
        # the Options Flow.
        version = 5

    if version < 6:
        # Minimum Device Runtime and Minimum Source Runtime were consolidated into a
        # single Minimum Runtime parameter. The prior Minimum Device Runtime value is
        # preserved under the new key, since it already represented the correct
        # "how long has the currently active device been running" semantics; Minimum
        # Source Runtime is discarded entirely - it no longer has any meaning.
        if "minimum_device_runtime" in data:
            data[CONF_MINIMUM_RUNTIME] = data.pop("minimum_device_runtime")

        data.pop("minimum_source_runtime", None)

        version = 6

    if version != entry.version or data != entry.data:
        hass.config_entries.async_update_entry(entry, data=data, version=version)

    return True


def _build_presets(data: dict) -> dict[str, PresetConfiguration]:
    # specs/23_preset_configuration.md §3 Preset Configuration
    return {
        preset: PresetConfiguration(
            heating_target_temperature=data[preset_data_key(preset, CONF_HEATING_TARGET)],
            cooling_target_temperature=data[preset_data_key(preset, CONF_COOLING_TARGET)],
            temperature_entity_id=data[preset_data_key(preset, CONF_TEMPERATURE_ENTITY)],
            humidity_entity_id=data.get(preset_data_key(preset, CONF_HUMIDITY_ENTITY)),
        )
        for preset in PRESETS
    }


async def async_setup_entry(hass: HomeAssistant, entry: SmartThermostatConfigEntry) -> bool:
    state_machine = StateMachine(ThermostatState.OFF)
    runtime_state = ThermostatRuntimeState()

    climate_control_algorithm = ClimateControlAlgorithm(
        configuration=ClimateControlAlgorithmConfiguration(
            kp=entry.data[CONF_KP],
            ti=entry.data[CONF_TI],
            tt=entry.data[CONF_TT],
            ts=entry.data[CONF_TS],
            tac_min=entry.data[CONF_TAC_MIN],
            tac_max=entry.data[CONF_TAC_MAX],
        ),
        state=ClimateControlAlgorithmState(),
        diagnostics_enabled=entry.data.get(CONF_ENABLE_CONTROL_DIAGNOSTICS, False),
    )

    thermostat_controller = ThermostatController(
        state_machine=state_machine,
        demand_engine=DemandEngine(),
        source_engine=SourceEngine(),
        protection_engine=ProtectionEngine(),
        transition_table=TransitionTable(),
        runtime_state=runtime_state,
        climate_control_algorithm=climate_control_algorithm,
    )

    entry.runtime_data = SmartThermostatRuntimeData(
        state_machine=state_machine,
        runtime_state=runtime_state,
        thermostat_controller=thermostat_controller,
        runtime_context_factory=RuntimeContextFactory(
            hass=hass,
            runtime_state=runtime_state,
            presets=_build_presets(entry.data),
        ),
        climate_controller=ClimateController(hass, entry.data[CONF_CLIMATE_DEVICE]),
        # specs/24_configuration_flow.md §4 Devices Step: the Boiler is always a
        # mandatory, real entity - exactly like the Climate Device.
        boiler_controller=BoilerController(hass, entry.data[CONF_BOILER]),
        climate_control_algorithm=climate_control_algorithm,
    )

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def _async_update_listener(hass: HomeAssistant, entry: SmartThermostatConfigEntry) -> None:
    # specs/25_options_flow.md §4 Runtime Behaviour
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: SmartThermostatConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
