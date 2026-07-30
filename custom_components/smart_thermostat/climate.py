import time
from datetime import datetime, timedelta
from typing import Any

from homeassistant.components.climate import (
    ATTR_CURRENT_TEMPERATURE,
    ATTR_TARGET_TEMP_HIGH,
    ATTR_TARGET_TEMP_LOW,
    PRESET_AWAY,
    PRESET_HOME,
    PRESET_SLEEP,
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.const import (
    ATTR_TEMPERATURE,
    CONF_NAME,
    PRECISION_TENTHS,
    PRECISION_WHOLE,
    STATE_OFF,
    STATE_ON,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
    UnitOfTemperature,
)
from homeassistant.core import CALLBACK_TYPE, Event, EventStateChangedData, HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import (
    async_call_later,
    async_track_state_change_event,
    async_track_time_interval,
)

from .boiler_controller import BoilerController
from .climate_controller import ClimateController
from .config_flow import (
    CONF_BOILER,
    CONF_CLIMATE_DEVICE,
    CONF_ENABLE_CONTROL_DIAGNOSTICS,
    CONF_INSTANTANEOUS_ENERGY_SURPLUS,
    CONF_MINIMUM_ENERGY_SURPLUS,
    CONF_MINIMUM_RUNTIME,
    CONF_SHUTDOWN_DELAY,
    CONF_SOURCE_CHANGE_DELAY,
    CONF_THERMOSTAT_TOLERANCE,
)
from .const import LEGACY_PRESET_NIGHT, control_diagnostics_signal
from .device_action import (
    ClimateHVACMode,
    DeviceAction,
    PowerState,
    SetClimateHVACMode,
    SetClimateTargetTemperature,
    TurnBoilerOff,
    TurnBoilerOn,
    TurnClimateOff,
    TurnClimateOn,
)
from .runtime_context import RuntimeContext
from .runtime_context_factory import RuntimeContextFactory
from .runtime_data import SmartThermostatConfigEntry, SmartThermostatRuntimeData
from .state_machine import StateMachine, ThermostatState
from .target_mode import TargetMode
from .thermostat_controller import ThermostatController, ThermostatControllerResult
from .thermostat_runtime_state import CurrentOperation

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
                climate_controller=entry.runtime_data.climate_controller,
                runtime_data=entry.runtime_data,
                boiler_entity_id=entry.data[CONF_BOILER],
                climate_entity_id=entry.data[CONF_CLIMATE_DEVICE],
                unique_id=entry.entry_id,
                entry_id=entry.entry_id,
                diagnostics_enabled=entry.data.get(CONF_ENABLE_CONTROL_DIAGNOSTICS, False),
                name=entry.data[CONF_NAME],
                instantaneous_energy_surplus_entity_id=entry.data[CONF_INSTANTANEOUS_ENERGY_SURPLUS],
                minimum_energy_surplus_entity_id=entry.data[CONF_MINIMUM_ENERGY_SURPLUS],
                hysteresis=entry.data[CONF_THERMOSTAT_TOLERANCE],
                minimum_runtime=_duration_to_seconds(entry.data[CONF_MINIMUM_RUNTIME]),
                shutdown_delay=_duration_to_seconds(entry.data[CONF_SHUTDOWN_DELAY]),
                source_change_delay=_duration_to_seconds(entry.data[CONF_SOURCE_CHANGE_DELAY]),
            )
        ]
    )


class SmartThermostatClimateEntity(ClimateEntity):
    # HVAC
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT_COOL]

    # specs/23_preset_configuration.md §2 Supported Presets
    _attr_preset_modes = [PRESET_HOME, PRESET_AWAY, PRESET_SLEEP]

    # Supported Features
    # specs/23_preset_configuration.md: the Climate Entity shall always expose the
    # effective Heating Target / Cooling Target of the active Preset, which requires the
    # standard Home Assistant target-temperature-range interface to be declared.
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
        climate_controller: ClimateController,
        runtime_data: SmartThermostatRuntimeData,
        boiler_entity_id: str,
        climate_entity_id: str,
        unique_id: str,
        entry_id: str,
        diagnostics_enabled: bool,
        name: str,
        instantaneous_energy_surplus_entity_id: str,
        minimum_energy_surplus_entity_id: str,
        hysteresis: float,
        minimum_runtime: float,
        shutdown_delay: float,
        source_change_delay: float,
    ) -> None:
        self._thermostat_controller = thermostat_controller
        self._runtime_context_factory = runtime_context_factory
        self._state_machine = state_machine
        self._boiler_controller = boiler_controller
        self._climate_controller = climate_controller
        self._runtime_data = runtime_data
        self._boiler_entity_id = boiler_entity_id
        self._climate_entity_id = climate_entity_id
        self._entry_id = entry_id
        # Control Diagnostics feature
        self._diagnostics_enabled = diagnostics_enabled

        self._instantaneous_energy_surplus_entity_id = instantaneous_energy_surplus_entity_id
        self._minimum_energy_surplus_entity_id = minimum_energy_surplus_entity_id
        self._hysteresis = hysteresis
        self._minimum_runtime = minimum_runtime
        self._shutdown_delay = shutdown_delay
        self._source_change_delay = source_change_delay

        # General
        self._attr_name: str | None = name
        self._attr_unique_id: str | None = unique_id
        self._attr_available: bool = True

        # Temperature
        self._attr_current_temperature: float | None = None
        self._attr_current_humidity: float | None = None
        # specs/26_target_mode.md §10: these always mirror the effective Heating Target /
        # Cooling Target resolved by the Runtime Context Factory according to the active
        # Target Mode (Preset or Manual) - they are never written independently.
        self._attr_target_temperature_high: float | None = None
        self._attr_target_temperature_low: float | None = None

        # specs/26_target_mode.md §5 Initial State / §13 Climate Entity
        self._target_mode: TargetMode = TargetMode.PRESET
        self._manual_heating_target: float | None = None
        self._manual_cooling_target: float | None = None

        # HVAC
        self._attr_hvac_mode: HVACMode = HVACMode.OFF
        self._attr_hvac_action: HVACAction | None = None

        # Presets
        # specs/23_preset_configuration.md §2: the active Preset always determines the
        # environmental inputs and comfort targets used by the Thermostat Controller, so
        # a concrete default (rather than None) is required for the thermostat to operate.
        self._attr_preset_mode: str = PRESET_HOME

        # specs/22_scheduled_evaluation_workflow.md §4 Climate Entity Responsibility
        self._scheduled_evaluation_cancel: CALLBACK_TYPE | None = None

        # specs/27_climate_control_architecture.md §11 Evaluation Workflow: the Climate
        # Control Algorithm's dedicated 30-second scheduler. Independent from the
        # one-shot Scheduled Evaluation Workflow above - this one repeats for as long as
        # Climate Regulation stays active and is the exclusive trigger of PI iterations.
        self._climate_regulation_scheduler_cancel: CALLBACK_TYPE | None = None
        # The most recently resolved Runtime Context / requested operation, kept fresh by
        # every event-driven async_evaluate() cycle. The periodic scheduler only ever
        # reads from this cache - it never derives or fetches anything itself.
        self._latest_context: RuntimeContext | None = None
        self._latest_requested_operation: CurrentOperation | None = None

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()

        self.async_on_remove(self._cancel_scheduled_evaluation)
        self.async_on_remove(self._stop_climate_regulation_scheduler)

        tracked_entity_ids = [
            self._instantaneous_energy_surplus_entity_id,
            self._minimum_energy_surplus_entity_id,
            self._climate_entity_id,
            self._boiler_entity_id,
            *self._runtime_context_factory.entity_ids_to_track,
        ]

        self.async_on_remove(
            async_track_state_change_event(
                self.hass,
                tracked_entity_ids,
                self._async_handle_tracked_state_change,
            )
        )

        await self.async_evaluate(reason="entity startup")

    async def _async_handle_tracked_state_change(self, event: Event[EventStateChangedData]) -> None:
        entity_id = event.data["entity_id"]
        await self.async_evaluate(reason=f"tracked entity change ({entity_id})")

    @property
    def temperature_unit(self) -> str:
        return self.hass.config.units.temperature_unit

    @property
    def precision(self) -> float:
        if self.temperature_unit == UnitOfTemperature.CELSIUS:
            return PRECISION_TENTHS
        return PRECISION_WHOLE

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        # specs/21_external_state_transitions.md §3 Enabling the Thermostat
        if hvac_mode == HVACMode.HEAT_COOL and self._state_machine.current_state == ThermostatState.OFF:
            self._state_machine.transition_to(ThermostatState.IDLE)

        self._attr_hvac_mode = hvac_mode
        await self.async_evaluate(reason="HVAC mode change")

    async def async_turn_on(self) -> None:
        await self.async_set_hvac_mode(HVACMode.HEAT_COOL)

    async def async_turn_off(self) -> None:
        await self.async_set_hvac_mode(HVACMode.OFF)

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        # specs/23_preset_configuration.md §7 Climate Entity
        # specs/26_target_mode.md §8 Preset Activation: selecting a Preset always
        # terminates Manual Target Mode. The stored Manual targets are left untouched.

        # Backward compatibility: the custom "night" preset identifier was replaced by
        # the standard Home Assistant "sleep" preset. Any caller (automation, script,
        # dashboard) still requesting the old identifier is transparently redirected -
        # no user intervention required, no behavioural difference from selecting Sleep
        # directly.
        if preset_mode == LEGACY_PRESET_NIGHT:
            preset_mode = PRESET_SLEEP

        self._attr_preset_mode = preset_mode
        self._target_mode = TargetMode.PRESET
        await self.async_evaluate(reason="preset change")

    async def async_set_temperature(self, **kwargs: Any) -> None:
        # specs/26_target_mode.md §6/§7 Manual Activation / Manual Target Updates
        # Only the Manual targets are updated here; the active Preset and its configured
        # targets are never touched, satisfying the single-source-of-truth invariant.
        if ATTR_TARGET_TEMP_LOW in kwargs:
            self._manual_heating_target = kwargs[ATTR_TARGET_TEMP_LOW]
        elif self._manual_heating_target is None:
            # First-ever Manual activation without an explicit low value: seed it from
            # whatever is currently displayed (the Preset's effective value up to now).
            self._manual_heating_target = self._attr_target_temperature_low

        if ATTR_TARGET_TEMP_HIGH in kwargs:
            self._manual_cooling_target = kwargs[ATTR_TARGET_TEMP_HIGH]
        elif self._manual_cooling_target is None:
            self._manual_cooling_target = self._attr_target_temperature_high

        self._target_mode = TargetMode.MANUAL
        await self.async_evaluate(reason="manual temperature change")

    def _read_required_value(self, entity_id: str) -> float | None:
        state = self.hass.states.get(entity_id)

        if state is None or state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            return None

        try:
            return float(state.state)
        except ValueError:
            return None

    def _read_boiler_power_state(self) -> PowerState | None:
        state = self.hass.states.get(self._boiler_entity_id)

        if state is None or state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            return None

        if state.state == STATE_ON:
            return PowerState.ON

        if state.state == STATE_OFF:
            return PowerState.OFF

        return None

    def _read_climate_device_snapshot(
        self, entity_id: str
    ) -> tuple[PowerState, ClimateHVACMode, float] | None:
        state = self.hass.states.get(entity_id)

        if state is None or state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            return None

        if state.state == HVACMode.OFF:
            power_state = PowerState.OFF
            hvac_mode = ClimateHVACMode.HEAT
        elif state.state == HVACMode.HEAT:
            power_state = PowerState.ON
            hvac_mode = ClimateHVACMode.HEAT
        elif state.state == HVACMode.COOL:
            power_state = PowerState.ON
            hvac_mode = ClimateHVACMode.COOL
        else:
            return None

        target_temperature = state.attributes.get(ATTR_TEMPERATURE)

        if target_temperature is None:
            return None

        try:
            target_temperature = float(target_temperature)
        except (TypeError, ValueError):
            return None

        return power_state, hvac_mode, target_temperature

    def _read_climate_device_internal_temperature(self, entity_id: str) -> float | None:
        # Control Diagnostics feature only: purely observational, optional ("if
        # available"), never a mandatory input - absence never blocks an evaluation.
        state = self.hass.states.get(entity_id)

        if state is None:
            return None

        internal_temperature = state.attributes.get(ATTR_CURRENT_TEMPERATURE)

        if internal_temperature is None:
            return None

        try:
            return float(internal_temperature)
        except (TypeError, ValueError):
            return None

    def _cancel_scheduled_evaluation(self) -> None:
        # specs/22_scheduled_evaluation_workflow.md §4 Climate Entity Responsibility / §6 Callback Replacement
        if self._scheduled_evaluation_cancel is not None:
            self._scheduled_evaluation_cancel()
            self._scheduled_evaluation_cancel = None

    async def _async_scheduled_evaluation_callback(self, _now: datetime) -> None:
        self._scheduled_evaluation_cancel = None
        await self.async_evaluate(reason="scheduled evaluation")

    async def _async_handle_scheduled_evaluation(self, result: ThermostatControllerResult) -> None:
        # specs/22_scheduled_evaluation_workflow.md §4 Climate Entity Responsibility / §5 Delayed Evaluations
        if result.next_evaluation_at is None:
            # No scheduling information present: the unconditional cancellation at the top
            # of async_evaluate() already guarantees no obsolete callback remains.
            return

        remaining = result.next_evaluation_at - time.monotonic()

        if remaining <= 0:
            # Immediate follow-up evaluation (e.g. HEATING/COOLING -> STOPPING): no callback
            # is created, execute exactly one additional evaluation right away.
            await self.async_evaluate(reason="immediate follow-up evaluation")
            return

        # Delayed evaluation: exactly one one-shot callback, never earlier than required.
        self._scheduled_evaluation_cancel = async_call_later(
            self.hass, remaining, self._async_scheduled_evaluation_callback
        )

    def _start_climate_regulation_scheduler(self) -> bool:
        # specs/27_climate_control_architecture.md §11 Evaluation Workflow: starts the
        # dedicated 30-second scheduler exactly once, on the transition into Climate
        # Regulation being active. A tick already in progress is left alone so the
        # cadence stays stable for as long as regulation remains active. Returns True
        # only on that transition (not-running -> running), so the caller can trigger
        # the immediate first iteration exactly once, never on subsequent cycles where
        # regulation was already active.
        if self._climate_regulation_scheduler_cancel is not None:
            return False

        self._climate_regulation_scheduler_cancel = async_track_time_interval(
            self.hass, self._async_climate_regulation_tick, timedelta(seconds=30)
        )
        return True

    def _stop_climate_regulation_scheduler(self) -> None:
        # specs/27_climate_control_architecture.md §11 Evaluation Workflow: stops the
        # scheduler immediately once Climate Regulation is no longer active. No further
        # PI iterations shall occur until it is started again.
        if self._climate_regulation_scheduler_cancel is not None:
            self._climate_regulation_scheduler_cancel()
            self._climate_regulation_scheduler_cancel = None

    async def _async_climate_regulation_tick(self, _now: datetime) -> None:
        # specs/27_climate_control_architecture.md §11 Evaluation Workflow: the ONLY
        # method in the entire integration allowed to invoke
        # ClimateControlAlgorithm.evaluate(). It reads the latest Runtime Context cached
        # by the event-driven pipeline rather than deriving or re-resolving anything
        # itself - Target Mode / Preset resolution remains solely owned by the Runtime
        # Context Factory.
        if self._latest_context is None or self._latest_requested_operation is None:
            return

        room_target_temperature = (
            self._latest_context.cooling_target_temperature
            if self._latest_requested_operation == CurrentOperation.COOLING
            else self._latest_context.heating_target_temperature
        )
        climate_device_internal_temperature = self._read_climate_device_internal_temperature(
            self._climate_entity_id
        )

        self._runtime_data.climate_control_algorithm.evaluate(
            room_target_temperature=room_target_temperature,
            room_temperature=self._latest_context.current_temperature,
            climate_device_internal_temperature=climate_device_internal_temperature,
        )

        # Propagate the freshly computed output into a Requested Device Action through
        # the normal, unchanged event-driven pipeline. ThermostatController.evaluate() no
        # longer invokes the PI controller itself - it only reads whatever output was
        # just produced above - so this call cannot cause a second iteration.
        await self.async_evaluate(reason="climate regulation tick")

    def _publish_diagnostics_availability(self, available: bool) -> None:
        # Control Diagnostics feature: mirrors this Climate Entity's own availability so
        # diagnostic sensors follow the Smart Thermostat's lifecycle, then notifies them
        # to refresh. No snapshot is recalculated or created by this call.
        if not self._diagnostics_enabled:
            return

        self._runtime_data.climate_entity_available = available
        async_dispatcher_send(self.hass, control_diagnostics_signal(self._entry_id))

    async def async_evaluate(self, reason: str = "unspecified") -> None:
        # specs/22_scheduled_evaluation_workflow.md §7 External Events
        self._cancel_scheduled_evaluation()

        instantaneous_energy_surplus = self._read_required_value(self._instantaneous_energy_surplus_entity_id)
        minimum_energy_surplus = self._read_required_value(self._minimum_energy_surplus_entity_id)
        current_boiler_power_state = self._read_boiler_power_state()
        climate_device_snapshot = self._read_climate_device_snapshot(self._climate_entity_id)

        if (
            instantaneous_energy_surplus is None
            or minimum_energy_surplus is None
            or current_boiler_power_state is None
            or climate_device_snapshot is None
        ):
            self._attr_available = False
            self.async_write_ha_state()
            self._publish_diagnostics_availability(False)
            self._latest_context = None
            self._latest_requested_operation = None
            self._stop_climate_regulation_scheduler()
            return

        (
            current_climate_power_state,
            current_climate_hvac_mode,
            current_climate_target_temperature,
        ) = climate_device_snapshot

        # specs/23_preset_configuration.md §4 Runtime Context
        # specs/26_target_mode.md §10/§15 Runtime Context Factory resolution
        context = self._runtime_context_factory.create(
            active_preset=self._attr_preset_mode,
            target_mode=self._target_mode,
            manual_heating_target_temperature=self._manual_heating_target,
            manual_cooling_target_temperature=self._manual_cooling_target,
            current_state=self._state_machine.current_state,
            hysteresis=self._hysteresis,
            instantaneous_energy_surplus=instantaneous_energy_surplus,
            minimum_energy_surplus=minimum_energy_surplus,
            now=time.monotonic(),
            minimum_runtime=self._minimum_runtime,
            shutdown_delay=self._shutdown_delay,
            source_change_delay=self._source_change_delay,
            current_boiler_power_state=current_boiler_power_state,
            current_climate_power_state=current_climate_power_state,
            current_climate_hvac_mode=current_climate_hvac_mode,
            current_climate_target_temperature=current_climate_target_temperature,
        )

        if context is None:
            self._attr_available = False
            self.async_write_ha_state()
            self._publish_diagnostics_availability(False)
            self._latest_context = None
            self._latest_requested_operation = None
            self._stop_climate_regulation_scheduler()
            return

        result = self._thermostat_controller.evaluate(
            context,
            enabled=self._attr_hvac_mode != HVACMode.OFF,
        )

        # specs/27_climate_control_architecture.md §11 Evaluation Workflow: kept fresh by
        # every event-driven cycle so the periodic Climate Regulation scheduler can read
        # the latest values without deriving or re-resolving anything itself.
        self._latest_context = context
        self._latest_requested_operation = result.requested_operation

        self._attr_available = True
        self._attr_current_temperature = context.current_temperature
        self._attr_current_humidity = context.current_humidity
        self._attr_target_temperature_low = context.heating_target_temperature
        self._attr_target_temperature_high = context.cooling_target_temperature
        self._attr_hvac_action = _HVAC_ACTION_MAP[(result.current_state, result.current_operation)]

        self.async_write_ha_state()
        self._publish_diagnostics_availability(True)

        await self._async_execute_requested_device_actions(result)

        # specs/27_climate_control_architecture.md §11 Evaluation Workflow: the scheduler
        # starts exactly when Climate Regulation becomes active and stops immediately
        # when it stops. No controller iterations shall occur while it is inactive.
        if result.climate_regulation_active:
            scheduler_just_started = self._start_climate_regulation_scheduler()
        else:
            scheduler_just_started = False
            self._stop_climate_regulation_scheduler()

        await self._async_handle_scheduled_evaluation(result)

        if scheduler_just_started:
            # specs/27_climate_control_architecture.md §11.2: the immediate iteration on
            # activation IS the first scheduler iteration, not a separate trigger - it
            # reuses the exact same tick method the 30-second timer calls, invoked once,
            # right after this cycle has fully settled (state, scheduling, diagnostics).
            # The controller therefore remains exclusively scheduler-driven.
            await self._async_climate_regulation_tick(datetime.now())

    async def _async_execute_requested_device_actions(self, result: ThermostatControllerResult) -> None:
        for action in result.requested_device_actions:
            await self._async_execute_device_action(action)

    async def _async_execute_device_action(self, action: DeviceAction) -> None:
        if isinstance(action, TurnBoilerOn):
            await self._boiler_controller.turn_on()
        elif isinstance(action, TurnBoilerOff):
            await self._boiler_controller.turn_off()
        elif isinstance(action, TurnClimateOn):
            await self._climate_controller.turn_on()
        elif isinstance(action, TurnClimateOff):
            await self._climate_controller.turn_off()
        elif isinstance(action, SetClimateHVACMode):
            await self._climate_controller.set_hvac_mode(_CLIMATE_HVAC_MODE_MAP[action.hvac_mode])
        elif isinstance(action, SetClimateTargetTemperature):
            await self._climate_controller.set_target_temperature(action.target_temperature)
