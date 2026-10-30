# Smart Thermostat

## Thermostat Runtime State Management

Version: 1.3

Status: Frozen

---

# 1. Purpose

This document defines how the Thermostat Runtime State is created, stored, shared and destroyed.

It also defines ownership of the runtime state instance and modification responsibilities.

The Thermostat Runtime State is part of the integration runtime.

It is not part of the Runtime Context.

---

# 2. Instance Lifecycle

Exactly one Thermostat Runtime State SHALL exist for each thermostat instance.

The instance SHALL be created during:

- async_setup_entry()

The instance SHALL be initialized with its default values.

specs/29_restart_recovery.md defines an exception to this: once the Climate Entity is added to Home Assistant, its own restart-recovery step MAY overwrite the freshly-defaulted instance's fields with previously-persisted values, before the first evaluation ever runs. This is not a modification performed during normal operation - it happens exactly once, before any Thermostat Controller evaluation has occurred against this instance, and only when the persisted data validates according to specs/29_restart_recovery.md §3. When it does not validate, the instance keeps its default values exactly as described above.

The same instance SHALL be reused throughout the lifetime of the integration.

---

# 3. Instance Ownership

The Smart Thermostat integration owns the Thermostat Runtime State instance.

The instance SHALL be stored inside the integration runtime data.

The integration is responsible for:

- creating the instance;
- storing the instance;
- sharing the instance with authorized components;
- releasing the instance during integration unload.

The integration never modifies its contents.

---

# 4. Modification Ownership

During normal operation - every evaluation cycle after the Climate Entity has been added to Home Assistant - the Thermostat Controller is the only component authorized to modify the Thermostat Runtime State.

No other component may update its contents during normal operation.

This includes every persistent runtime field, including:

- Current Heating Source;
- Current Operation;
- Device Started At;
- Demand Ended At;
- Source Selected At;
- Desired Source Differs Since.

In particular, during normal operation:

- Runtime Context Factory: read-only
- Climate Entity: read-only
- Device Controllers: no access
- State Machine: no access
- Domain Engines: no access

The Thermostat Controller SHALL apply updates according to:

- specs/15_runtime_state_update_rules.md

specs/29_restart_recovery.md defines the single exception to this exclusivity: during Climate Entity startup, before the first Thermostat Controller evaluation has ever run against this instance, the Climate Entity's restart-recovery step MAY set the Thermostat Runtime State's fields directly from validated persisted data. This is restoration of the instance's initial values, not a modification performed during normal operation, and it never occurs after the first evaluation has run.

---

# 5. Runtime Context Creation

For every evaluation cycle:

1. The Runtime Context Factory reads:
   - Home Assistant entity states;
   - Config Entry values;
   - Thermostat Runtime State.

2. The Runtime Context Factory creates a new immutable Runtime Context.

3. The Runtime Context is passed to the Thermostat Controller.

The Runtime Context contains a snapshot of the current Thermostat Runtime State.

---

# 6. Runtime Evaluation

During the evaluation:

- the Runtime Context remains immutable;
- the Thermostat Runtime State remains unchanged.

Only after the evaluation has completed successfully may the Thermostat Controller update the Thermostat Runtime State.

The Runtime Context is never updated after creation.

---

# 7. Failed Evaluation

If the evaluation fails:

- the Runtime Context is discarded;
- the Thermostat Runtime State SHALL remain unchanged.

Partial Runtime State updates are not allowed.

---

# 8. Integration Unload

During:

- async_unload_entry()

the integration releases the Thermostat Runtime State instance together with all other runtime objects.

No runtime information survives integration unloading *as an in-memory object*.

This does not preclude the Climate Entity from having separately persisted a representation of that information beforehand, through Home Assistant's native `RestoreEntity` mechanism, for the sole purpose of restoring a new instance's initial values on the next startup (specs/29_restart_recovery.md). That persisted representation is not the Thermostat Runtime State instance itself, is never read by anything during normal operation, and only ever influences the initial values of the next instance created by a subsequent `async_setup_entry()` call.

---

# 9. Design Principles

The Thermostat Runtime State is the single source of truth for persistent runtime information.

This includes every runtime value that must survive across multiple evaluation cycles.

The Runtime Context is a temporary immutable snapshot built from:

- Home Assistant runtime information;
- Config Entry values;
- Thermostat Runtime State.

The Runtime Context never owns persistent information.

The Thermostat Runtime State never contains Home Assistant objects.

Instance ownership and modification ownership are intentionally separated.

The integration owns the lifetime of the instance.

The Thermostat Controller owns every modification of its contents.

---

# 10. Source of Truth

This document defines the lifecycle and management of the Thermostat Runtime State.

Every implementation shall strictly follow this specification.