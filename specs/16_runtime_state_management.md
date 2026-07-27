# Smart Thermostat

## Thermostat Runtime State Management

Version: 1.2

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

The Thermostat Controller is the only component authorized to modify the Thermostat Runtime State.

No other component may update its contents.

This includes every persistent runtime field, including:

- Current Heating Source;
- Current Operation;
- Device Started At;
- Demand Ended At;
- Source Selected At;
- Desired Source Differs Since.

In particular:

- Runtime Context Factory: read-only
- Climate Entity: read-only
- Device Controllers: no access
- State Machine: no access
- Domain Engines: no access

The Thermostat Controller SHALL apply updates according to:

- specs/15_runtime_state_update_rules.md

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

No runtime information survives integration unloading.

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