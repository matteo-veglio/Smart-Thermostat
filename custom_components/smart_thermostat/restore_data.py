"""specs/29_restart_recovery.md

Isolates the RestoreEntity persistence shape and the wall-clock <-> monotonic
timestamp reconstruction needed to restore Thermostat Runtime State and PI state
across a Home Assistant restart. Kept as a small, dedicated module so this concern
never spreads into the Climate Entity's evaluation logic or into the controller/
algorithm classes themselves - it only ever produces or consumes plain, validated
values and never touches ThermostatController, ProtectionEngine, or the PI equations.

Two independent restoration tiers are defined here, matching specs/29_restart_
recovery.md §2/§3:

- User Intent (HVAC mode is restored directly in climate.py from the entity's own
  last plain state; Preset Mode, Target Mode and the Manual targets are restored here,
  leniently, field by field).
- Runtime/PI Bundle (ThermostatState, Current Operation, Current Heating Source, the
  four protection timestamps, i_prev, desat_prev): restored atomically - either every
  field validates and all of them are applied together, or none of them are.

A persisted payload is always treated as untrusted (specs/29 §6 Safe Failure
Behaviour): every parse function returns None rather than raising when the data is
missing, malformed, or from an incompatible schema version.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from homeassistant.helpers.restore_state import ExtraStoredData
from homeassistant.util import dt as dt_util

from .source_engine import HeatingSource
from .state_machine import ThermostatState
from .target_mode import TargetMode
from .thermostat_runtime_state import CurrentOperation

# Bumped only if the persisted shape changes incompatibly. A mismatch is treated as
# missing data (specs/29 §6) rather than attempting a migration.
SCHEMA_VERSION = 1


def monotonic_to_wall(value: float, *, mono_now: float, wall_now: datetime) -> str | None:
    """Convert a monotonic timestamp (0.0 meaning "unset") into the ISO 8601
    wall-clock instant it corresponded to, computed against the given
    (monotonic, wall-clock) reference pair captured at the same moment."""
    if value == 0.0:
        return None

    return (wall_now - timedelta(seconds=mono_now - value)).isoformat()


def wall_to_monotonic(value: str | None, *, mono_now: float, wall_now: datetime) -> float:
    """Reconstruct an equivalent monotonic timestamp from a previously saved
    wall-clock instant, anchored against a fresh (monotonic, wall-clock) reference
    pair, so that elapsed real time - not elapsed process uptime - continues
    unaffected by the restart. Returns 0.0 (the domain's own "unset" sentinel) for
    anything absent or unparseable."""
    if value is None:
        return 0.0

    saved_wall = dt_util.parse_datetime(value)

    if saved_wall is None:
        return 0.0

    elapsed = (wall_now - saved_wall).total_seconds()
    return mono_now - elapsed


@dataclass(frozen=True)
class RestoredUserIntent:
    """specs/29_restart_recovery.md §2 User Intent - restored leniently, field by
    field. Each field independently falls back to None (meaning: the Climate Entity
    keeps its own existing default) rather than a missing/invalid field invalidating
    the others."""

    target_mode: TargetMode | None
    preset_mode: str | None
    manual_heating_target: float | None
    manual_cooling_target: float | None


@dataclass(frozen=True)
class RestoredRuntimeBundle:
    """specs/29_restart_recovery.md §3 Runtime/PI Bundle - restored atomically. Every
    field here is guaranteed valid whenever an instance of this class exists; see
    parse_runtime_bundle()."""

    thermostat_state: ThermostatState
    current_operation: CurrentOperation
    current_heating_source: HeatingSource
    device_started_at: float
    demand_ended_at: float
    source_selected_at: float
    desired_source_differs_since: float
    i_prev: float
    desat_prev: float


@dataclass
class SmartThermostatExtraStoredData(ExtraStoredData):
    """The complete Home Assistant RestoreEntity extra-data payload for one Smart
    Thermostat instance. A pure data container - it performs no validation itself.
    Validation happens in parse_user_intent()/parse_runtime_bundle() when a
    previously-restored dict is consumed, since persisted data must always be
    treated as untrusted (specs/29 §6)."""

    schema_version: int
    target_mode: str | None
    preset_mode: str | None
    manual_heating_target: float | None
    manual_cooling_target: float | None
    thermostat_state: str | None
    current_operation: str | None
    current_heating_source: str | None
    device_started_at: str | None
    demand_ended_at: str | None
    source_selected_at: str | None
    desired_source_differs_since: str | None
    i_prev: float | None
    desat_prev: float | None

    def as_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


def build_extra_stored_data(
    *,
    target_mode: TargetMode,
    preset_mode: str,
    manual_heating_target: float | None,
    manual_cooling_target: float | None,
    thermostat_state: ThermostatState,
    current_operation: CurrentOperation,
    current_heating_source: HeatingSource,
    device_started_at: float,
    demand_ended_at: float,
    source_selected_at: float,
    desired_source_differs_since: float,
    i_prev: float,
    desat_prev: float,
    mono_now: float,
    wall_now: datetime,
) -> SmartThermostatExtraStoredData:
    """Build the payload returned from the Climate Entity's extra_restore_state_data
    property. Called every time Home Assistant snapshots this entity's extra data -
    always reflects whatever the Runtime State/PI state hold at that instant."""
    return SmartThermostatExtraStoredData(
        schema_version=SCHEMA_VERSION,
        target_mode=target_mode.value,
        preset_mode=preset_mode,
        manual_heating_target=manual_heating_target,
        manual_cooling_target=manual_cooling_target,
        thermostat_state=thermostat_state.value,
        current_operation=current_operation.value,
        current_heating_source=current_heating_source.value,
        device_started_at=monotonic_to_wall(device_started_at, mono_now=mono_now, wall_now=wall_now),
        demand_ended_at=monotonic_to_wall(demand_ended_at, mono_now=mono_now, wall_now=wall_now),
        source_selected_at=monotonic_to_wall(source_selected_at, mono_now=mono_now, wall_now=wall_now),
        desired_source_differs_since=monotonic_to_wall(
            desired_source_differs_since, mono_now=mono_now, wall_now=wall_now
        ),
        i_prev=i_prev,
        desat_prev=desat_prev,
    )


def parse_user_intent(raw: dict[str, Any] | None) -> RestoredUserIntent | None:
    """specs/29 §2: lenient, field-by-field restoration. Returns None only if `raw`
    itself is missing, malformed, or from an incompatible schema version; individual
    fields inside an otherwise-valid payload fall back to None independently rather
    than invalidating the whole tier."""
    if not isinstance(raw, dict) or raw.get("schema_version") != SCHEMA_VERSION:
        return None

    return RestoredUserIntent(
        target_mode=_parse_enum(TargetMode, raw.get("target_mode")),
        preset_mode=raw.get("preset_mode") if isinstance(raw.get("preset_mode"), str) else None,
        manual_heating_target=_as_float_or_none(raw.get("manual_heating_target")),
        manual_cooling_target=_as_float_or_none(raw.get("manual_cooling_target")),
    )


def parse_runtime_bundle(
    raw: dict[str, Any] | None, *, mono_now: float, wall_now: datetime
) -> RestoredRuntimeBundle | None:
    """specs/29 §3: atomic, all-or-nothing restoration. Returns None - the caller
    MUST then apply the safe-fresh-state fallback - unless every field required to
    reconstruct a coherent regulation episode validates successfully."""
    if not isinstance(raw, dict) or raw.get("schema_version") != SCHEMA_VERSION:
        return None

    thermostat_state = _parse_enum(ThermostatState, raw.get("thermostat_state"))
    current_operation = _parse_enum(CurrentOperation, raw.get("current_operation"))
    current_heating_source = _parse_enum(HeatingSource, raw.get("current_heating_source"))
    i_prev = _as_float_or_none(raw.get("i_prev"))
    desat_prev = _as_float_or_none(raw.get("desat_prev"))

    if (
        thermostat_state is None
        or current_operation is None
        or current_heating_source is None
        or i_prev is None
        or desat_prev is None
    ):
        return None

    return RestoredRuntimeBundle(
        thermostat_state=thermostat_state,
        current_operation=current_operation,
        current_heating_source=current_heating_source,
        device_started_at=wall_to_monotonic(raw.get("device_started_at"), mono_now=mono_now, wall_now=wall_now),
        demand_ended_at=wall_to_monotonic(raw.get("demand_ended_at"), mono_now=mono_now, wall_now=wall_now),
        source_selected_at=wall_to_monotonic(raw.get("source_selected_at"), mono_now=mono_now, wall_now=wall_now),
        desired_source_differs_since=wall_to_monotonic(
            raw.get("desired_source_differs_since"), mono_now=mono_now, wall_now=wall_now
        ),
        i_prev=i_prev,
        desat_prev=desat_prev,
    )


def _parse_enum(enum_cls: type, value: Any) -> Any | None:
    if not isinstance(value, str):
        return None

    try:
        return enum_cls(value)
    except ValueError:
        return None


def _as_float_or_none(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None

    return float(value)
