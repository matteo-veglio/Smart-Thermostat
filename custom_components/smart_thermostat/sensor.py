from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .climate_control_algorithm import ClimateControlAlgorithm, ControllerDiagnosticsSnapshot
from .config_flow import CONF_ENABLE_CONTROL_DIAGNOSTICS
from .const import control_diagnostics_signal
from .runtime_data import SmartThermostatConfigEntry, SmartThermostatRuntimeData

_CELSIUS = "°C"


@dataclass(frozen=True, kw_only=True)
class _DiagnosticSensorDescription(SensorEntityDescription):
    value_fn: Callable[[ControllerDiagnosticsSnapshot], object] = lambda snapshot: None


# Control Diagnostics feature: one entry per Controller Diagnostics Snapshot field.
# Every sensor is a pure read-through - none of them perform any calculation.
SENSOR_DESCRIPTIONS: tuple[_DiagnosticSensorDescription, ...] = (
    _DiagnosticSensorDescription(
        key="room_temperature",
        name="Room Temperature",
        native_unit_of_measurement=_CELSIUS,
        value_fn=lambda s: s.room_temperature,
    ),
    _DiagnosticSensorDescription(
        key="room_target_temperature",
        name="Room Target Temperature",
        native_unit_of_measurement=_CELSIUS,
        value_fn=lambda s: s.room_target_temperature,
    ),
    _DiagnosticSensorDescription(
        key="climate_device_target_temperature",
        name="Climate Device Target Temperature",
        native_unit_of_measurement=_CELSIUS,
        value_fn=lambda s: s.climate_device_target_temperature,
    ),
    _DiagnosticSensorDescription(
        key="climate_device_internal_temperature",
        name="Climate Device Internal Temperature",
        native_unit_of_measurement=_CELSIUS,
        value_fn=lambda s: s.climate_device_internal_temperature,
    ),
    _DiagnosticSensorDescription(
        key="control_error",
        name="Control Error",
        native_unit_of_measurement=_CELSIUS,
        value_fn=lambda s: s.control_error,
    ),
    _DiagnosticSensorDescription(
        key="proportional_contribution",
        name="Proportional Contribution",
        native_unit_of_measurement=_CELSIUS,
        value_fn=lambda s: s.proportional_contribution,
    ),
    _DiagnosticSensorDescription(
        key="integral_contribution",
        name="Integral Contribution",
        native_unit_of_measurement=_CELSIUS,
        value_fn=lambda s: s.integral_contribution,
    ),
    _DiagnosticSensorDescription(
        key="pi_output",
        name="PI Output",
        native_unit_of_measurement=_CELSIUS,
        value_fn=lambda s: s.pi_output,
    ),
    _DiagnosticSensorDescription(
        key="feedforward_output",
        name="Feedforward Output",
        native_unit_of_measurement=_CELSIUS,
        value_fn=lambda s: s.feedforward_output,
    ),
    _DiagnosticSensorDescription(
        key="saturated_output",
        name="Saturated Output",
        native_unit_of_measurement=_CELSIUS,
        # Same underlying value as "Climate Device Target Temperature" (specs/28 §9 Step
        # 6 TAc_Set) - exposed a second time as its own sensor, per its distinct
        # conceptual meaning as a Controller Variable rather than a Process Variable.
        value_fn=lambda s: s.climate_device_target_temperature,
    ),
    _DiagnosticSensorDescription(
        key="anti_windup_desaturation",
        name="Anti-Windup Desaturation",
        native_unit_of_measurement=_CELSIUS,
        value_fn=lambda s: s.anti_windup_desaturation,
    ),
    _DiagnosticSensorDescription(
        key="feedforward_offset",
        name="Feedforward Offset",
        native_unit_of_measurement=_CELSIUS,
        value_fn=lambda s: s.feedforward_offset,
    ),
    _DiagnosticSensorDescription(
        key="controller_saturated",
        name="Controller Saturated",
        value_fn=lambda s: s.controller_saturated,
    ),
    _DiagnosticSensorDescription(
        key="controller_enabled",
        name="Controller Enabled",
        value_fn=lambda s: s.controller_enabled,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SmartThermostatConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    if not entry.data.get(CONF_ENABLE_CONTROL_DIAGNOSTICS, False):
        # Control Diagnostics disabled: no entities created, matching "no diagnostic
        # entities shall be created" and "no additional memory or processing shall be
        # used" - nothing below this line ever runs for this Config Entry.
        return

    async_add_entities(
        SmartThermostatDiagnosticSensor(entry, description) for description in SENSOR_DESCRIPTIONS
    )


class SmartThermostatDiagnosticSensor(SensorEntity):
    """A single passive read-through of one Controller Diagnostics Snapshot field.

    This entity never calculates, evaluates or duplicates any controller logic. It only
    reads the value already present in ClimateControlAlgorithm.last_snapshot.
    """

    _attr_should_poll = False
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_has_entity_name = True

    entity_description: _DiagnosticSensorDescription

    def __init__(self, entry: SmartThermostatConfigEntry, description: _DiagnosticSensorDescription) -> None:
        self.entity_description = description
        self._entry_id = entry.entry_id
        self._runtime_data: SmartThermostatRuntimeData = entry.runtime_data
        self._algorithm: ClimateControlAlgorithm = entry.runtime_data.climate_control_algorithm
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_name = description.name

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, control_diagnostics_signal(self._entry_id), self._handle_snapshot_updated
            )
        )

    @callback
    def _handle_snapshot_updated(self) -> None:
        self.async_write_ha_state()

    @property
    def native_value(self) -> object:
        snapshot = self._algorithm.last_snapshot

        if snapshot is None:
            return None

        return self.entity_description.value_fn(snapshot)

    @property
    def available(self) -> bool:
        return self._runtime_data.climate_entity_available and self._algorithm.last_snapshot is not None
