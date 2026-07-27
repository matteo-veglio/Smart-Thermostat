from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .boiler_controller import BoilerController
from .climate_control_table import DEFAULT_COOLING_TABLE, DEFAULT_HEATING_TABLE, ClimateControlTable
from .climate_controller import ClimateController
from .config_flow import CONF_COOLING_SOURCE, CONF_HEATING_SOURCE_1, CONF_HEATING_SOURCE_2
from .demand_engine import DemandEngine
from .protection_engine import ProtectionEngine
from .runtime_context_factory import RuntimeContextFactory
from .runtime_data import SmartThermostatConfigEntry, SmartThermostatRuntimeData
from .source_engine import SourceEngine
from .state_machine import StateMachine, ThermostatState
from .thermostat_controller import ThermostatController
from .thermostat_runtime_state import ThermostatRuntimeState
from .transition_table import TransitionTable

PLATFORMS: list[Platform] = [Platform.CLIMATE]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    return True


async def async_setup_entry(hass: HomeAssistant, entry: SmartThermostatConfigEntry) -> bool:
    state_machine = StateMachine(ThermostatState.OFF)
    runtime_state = ThermostatRuntimeState()

    thermostat_controller = ThermostatController(
        state_machine=state_machine,
        demand_engine=DemandEngine(),
        source_engine=SourceEngine(),
        protection_engine=ProtectionEngine(),
        transition_table=TransitionTable(),
        runtime_state=runtime_state,
        climate_control_table=ClimateControlTable(
            heating_table=DEFAULT_HEATING_TABLE,
            cooling_table=DEFAULT_COOLING_TABLE,
        ),
    )

    entry.runtime_data = SmartThermostatRuntimeData(
        state_machine=state_machine,
        runtime_state=runtime_state,
        thermostat_controller=thermostat_controller,
        runtime_context_factory=RuntimeContextFactory(runtime_state=runtime_state),
        boiler_controller=BoilerController(hass, entry.data[CONF_HEATING_SOURCE_1]),
        heating_climate_controller=ClimateController(hass, entry.data[CONF_HEATING_SOURCE_2]),
        cooling_climate_controller=ClimateController(hass, entry.data[CONF_COOLING_SOURCE]),
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: SmartThermostatConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
