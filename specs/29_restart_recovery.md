# Smart Thermostat

## Restart Recovery

Version: 1.0

Status: Frozen

---

# 1. Purpose

This document defines how the Smart Thermostat behaves across a Home Assistant restart, an integration reload, and an Options Flow reload.

A Home Assistant restart SHALL NOT be interpreted as the user requesting the thermostat to be turned off.

A Home Assistant restart SHALL NOT terminate a regulation episode that was still active.

This document defines exactly which state is restored, which state is intentionally never restored, and the safe fallback behaviour when persisted data is missing, corrupted or incompatible.

---

# 2. User Intent

The following values represent user intent and are restored leniently, field by field. A missing or invalid individual field falls back to its own default independently - it never invalidates the other fields.

- HVAC Mode
- Preset Mode
- Target Mode (Preset / Manual)
- Manual Heating Target
- Manual Cooling Target

HVAC Mode is restored from the Climate Entity's own previous state (Home Assistant's native entity state, not a bespoke payload).

Preset Mode, Target Mode and the Manual targets are restored from the Climate Entity's extra restore state data.

If the previous HVAC Mode cannot be determined, or is not a currently supported value, HVAC Mode SHALL fall back to OFF. No operating mode shall ever be invented.

---

# 3. Runtime/PI Bundle

The following values together represent one continuous regulation episode and SHALL be restored atomically - either every value below validates and all of them are applied together, or none of them are:

- Thermostat State
- Current Operation
- Current Heating Source
- Device Started At
- Demand Ended At
- Source Selected At
- Desired Source Differs Since
- PI Integral State (I_prev)
- PI Anti-Windup State (Desat_prev)

If any single field in this bundle is missing, malformed, an unrecognised enum value, or from an incompatible schema version, the entire bundle SHALL be discarded and every field in it SHALL fall back to the same fresh-installation defaults already used when no restore data exists at all (specs/16_runtime_state_management.md §2, specs/28_climate_control_mathematical_model.md §7).

Restoring this bundle SHALL NOT be treated as a Thermostat Controller evaluation, a state-machine transition, or a PI controller iteration. It only establishes the initial values that the first evaluation after restart - the existing, unmodified "entity startup" evaluation (specs/22_scheduled_evaluation_workflow.md) - observes. No new evaluation path is introduced.

---

# 4. Timestamp Reconstruction

Device Started At, Demand Ended At, Source Selected At and Desired Source Differs Since are measured against `time.monotonic()`, a clock that is relative to the current process and has no meaning across a restart.

These timestamps SHALL NOT be persisted as raw monotonic values.

For persistence, each timestamp SHALL be converted to the wall-clock instant it corresponds to, computed from a `(time.monotonic(), wall-clock now)` reference pair captured at the moment of saving. A timestamp equal to `0.0` (the domain's "unset" sentinel - specs/15_runtime_state_update_rules.md) SHALL be persisted as absent, not as a wall-clock value.

On restoration, each persisted wall-clock instant SHALL be converted back into an equivalent `time.monotonic()` value, computed from a fresh `(time.monotonic(), wall-clock now)` reference pair captured at the moment of restoring, so that the elapsed real-world time - not elapsed process uptime - continues unaffected by the restart.

Example: if Minimum Runtime is 60 seconds, Device Started At corresponded to wall-clock time T, and Home Assistant restarts 30 seconds later, the reconstructed Device Started At SHALL cause Minimum Runtime to require only the remaining 30 seconds, not a fresh 60-second wait.

This reconstruction happens once, during restoration, entirely inside the Home Assistant integration layer. The Protection Engine and the Thermostat Controller SHALL continue to receive and compare only `time.monotonic()`-based values exactly as before this feature existed. No second timing mechanism is introduced.

---

# 5. State Never Restored

The following SHALL never be persisted or restored, under any circumstance:

- the Climate Device's current physical power state;
- the Boiler's current physical power state;
- the Climate Device's actual reported HVAC mode;
- the Climate Device's actual reported target temperature;
- Control Diagnostics' last snapshot;
- the PI controller's last valid output;
- any scheduled-evaluation callback or its remaining delay.

Physical device state SHALL always be read from the live Home Assistant entities on every evaluation, including the first one after a restart. Restored logical state SHALL NEVER by itself cause a Requested Device Action - only a fresh evaluation against live conditions may do so (specs/17_requested_device_actions.md).

The PI controller's last valid output and Control Diagnostics' last snapshot are not restored because Climate Regulation's own activation logic (specs/27_climate_control_architecture.md §11.2) already guarantees an immediate, fresh iteration on the very first cycle regulation becomes active again after a restart - restoring them would add complexity without a corresponding benefit.

---

# 6. Safe Failure Behaviour

Persisted data SHALL always be treated as untrusted.

If restored data is missing, malformed, an unrecognised enum value, or from an incompatible schema version:

- HVAC Mode SHALL fall back to OFF;
- the Runtime/PI Bundle SHALL fall back to its fresh-installation defaults (Thermostat State IDLE or OFF as already established today, Current Operation NONE, PI Integral State and Anti-Windup State both `0.0`);
- Home Assistant startup SHALL never fail, block, or raise because of invalid restore data.

The thermostat SHALL then behave exactly as a fresh installation would.

---

# 7. Recovery Sequence

The recovery sequence SHALL be:

1. Home Assistant restores the Climate Entity's previous plain state and extra restore state data (native `RestoreEntity` mechanism).
2. User Intent (§2) is restored, leniently, field by field.
3. The Runtime/PI Bundle (§3) is restored atomically, or discarded entirely in favour of fresh defaults.
4. Every restored timestamp is reconstructed from monotonic/wall-clock reference pairs (§4).
5. The existing, unmodified "entity startup" evaluation runs exactly as it always has.
6. That evaluation reads live Home Assistant entity state, evaluates current demand, evaluates current source, and reconciles the restored logical state with current real-world conditions using the existing, unmodified Transition Table and Protection Engine.
7. Any Requested Device Action is generated exactly as on any other cycle, from this fresh comparison - never directly from restored data.

No step in this sequence introduces a new execution path, a new control algorithm, or a second source of truth for logical or PI state.

---

# 8. Integration Reload

Home Assistant provides no reliable way for an integration to distinguish a genuine process restart from an integration reload (for example, one triggered by an Options Flow change - specs/25_options_flow.md §4).

The recovery sequence defined in this document therefore applies identically to both. This is intentional: changing one configuration value SHALL NOT arbitrarily discard the user's selected HVAC Mode, the active regulation episode, or its PI state - unless the changed configuration itself makes the restored state invalid, in which case §6 Safe Failure Behaviour applies exactly as it would for any other invalid restore data.

---

# 9. Persistence Mechanism

Restart Recovery SHALL use Home Assistant's native `RestoreEntity` mechanism exclusively:

- the Climate Entity's own previous state, for User Intent's HVAC Mode;
- `RestoreEntity` extra restore state data, for the remainder of User Intent and for the entire Runtime/PI Bundle.

Config Entry data and Config Entry options SHALL NOT be used for any of the state described in this document. Configuration data represents user-configured, admin-managed settings; Runtime/PI state changes far more frequently and belongs exclusively to `RestoreEntity`'s storage. These two concepts SHALL remain completely separate.

The extra restore state data shape SHALL be defined in exactly one small, dedicated module, isolated from the Thermostat Controller, the Protection Engine, and the Climate Control Algorithm.

---

# 10. Source of Truth

This document defines the complete Restart Recovery behaviour of the Smart Thermostat.

Every implementation shall strictly follow this specification.
