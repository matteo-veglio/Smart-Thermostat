# Smart Thermostat

## Thermostat Runtime State Management

Version: 1.0

Status: Frozen

---

# 1. Purpose

This document defines how the Thermostat Runtime State is created, owned, shared and destroyed.

It specifies the lifecycle of the runtime state within the Smart Thermostat integration.

The Thermostat Runtime State is part of the integration runtime.

It is not part of the Runtime Context.

---

# 2. Creation

Exactly one Thermostat Runtime State SHALL exist for each thermostat instance.

The Thermostat Runtime State SHALL be created during the integration setup.

Creation occurs inside:

- async_setup_entry()

The Thermostat Runtime State SHALL be initialized with its default values.

---

# 3. Ownership

The Thermostat Runtime State is owned by the Smart Thermostat integration.

The integration keeps exactly one shared instance.

The Thermostat Controller is the only component allowed to modify it.

All other components shall treat it as read-only.

---

# 4. Storage

The Thermostat Runtime State SHALL be stored inside the integration runtime data.

It SHALL be available to:

- Runtime Context Factory (read-only)
- Thermostat Controller (read/write)

No other component shall require direct access.

---

# 5. Runtime Context Creation

For every evaluation cycle:

1. The Runtime Context Factory reads:
   - Home Assistant entity states;
   - Config Entry values;
   - Thermostat Runtime State.

2. The Runtime Context Factory creates a new immutable Runtime Context.

3. The Runtime Context is passed to the Thermostat Controller.

The Runtime Context contains a snapshot of the Thermostat Runtime State.

---

# 6. Runtime Evaluation

During the evaluation:

- the Runtime Context remains immutable;
- the Thermostat Runtime State remains unchanged.

Only after the evaluation has completed successfully may the Thermostat Controller update the Thermostat Runtime State according to:

- specs/15_runtime_state_update_rules.md

---

# 7. Failed Evaluation

If the evaluation fails for any reason:

- the Runtime Context is discarded;
- the Thermostat Runtime State SHALL NOT be modified;
- the previous Thermostat Runtime State remains valid.

Partial updates are not allowed.

---

# 8. Integration Unload

During:

- async_unload_entry()

the Thermostat Runtime State SHALL be released together with all other integration runtime objects.

No runtime state survives unloading the integration.

---

# 9. Design Principles

The Thermostat Runtime State is the single source of truth for persistent runtime information.

The Runtime Context is a temporary snapshot created from:

- Home Assistant;
- Config Entry;
- Thermostat Runtime State.

The Runtime Context never owns persistent information.

The Thermostat Runtime State never contains Home Assistant objects.

---

# 10. Source of Truth

This document defines the lifecycle and management of the Thermostat Runtime State.

Every implementation shall strictly follow this specification.