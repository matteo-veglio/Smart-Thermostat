# Smart Thermostat

## State Machine

Version: 2.3

Status: Frozen

---

# 1. Purpose

The State Machine represents the current operating state of the Smart Thermostat.

Its only responsibility is to represent the thermostat operating state.

The State Machine shall never:

- determine heating or cooling demand;
- select the heating source;
- communicate with Home Assistant;
- control any physical device;
- execute timers or protection logic.

These responsibilities belong to other components.

---

# 2. States

The thermostat can be in one of the following states.

| State | Description |
|--------|-------------|
| OFF | Thermostat disabled. |
| IDLE | Thermostat enabled but no heating or cooling demand exists. |
| STARTING | A new heating or cooling request has been accepted and the system is preparing to start. |
| HEATING | Active heating request. |
| COOLING | Active cooling request. |
| STOPPING | Heating or cooling has ended and the shutdown delay is active. |

---

# 3. Important Principle

The State Machine represents **only the logical operating state** of the thermostat.

It intentionally does **not** represent:

- which heating source is currently active;
- which cooling device is currently active;
- photovoltaic surplus conditions;
- controller decisions.

Heating source selection is managed exclusively by the Source Engine.

---

# 4. State Transitions

The following transitions are allowed.

| Current State | Next State |
|----------------|------------|
| OFF | IDLE |
| IDLE | OFF |
| IDLE | STARTING |
| STARTING | HEATING |
| STARTING | COOLING |
| STARTING | OFF |
| STARTING | IDLE |
| HEATING | STOPPING |
| COOLING | STOPPING |
| STOPPING | IDLE |
| STOPPING | OFF |
| STOPPING | STARTING |

Any transition not listed above shall be rejected.

STOPPING represents a shutdown that has been decided but not yet executed - the
controlled device remains physically active for as long as the thermostat stays in
STOPPING (see specs/11_controller_transition_table.md §8 and
specs/12_controller_protection_workflow.md §3). If demand returns before the shutdown
completes, the pending shutdown is cancelled and the thermostat resumes through
STARTING rather than waiting for IDLE.

STARTING → IDLE represents a cancelled startup: if the demand that caused STARTING
disappears before HEATING/COOLING is confirmed, the requested state becomes IDLE
(specs/11_controller_transition_table.md §7). Unlike STOPPING, the controlled device may
already have been commanded on during STARTING (see specs/12_controller_protection_
workflow.md §3), so this transition is subject to the same protection model as
STOPPING → IDLE rather than being immediate and ungated.

---

# 5. Invalid Transitions

The State Machine shall reject every transition not explicitly defined in this document.

Invalid transitions shall generate an exception.

The State Machine shall never silently ignore invalid transitions.

---

# 6. State Persistence

The current state shall be stored internally by the State Machine.

No persistence to Home Assistant is performed by this component.

Persistence across Home Assistant restarts is the responsibility of higher-level components. specs/29_restart_recovery.md defines this responsibility completely: the Climate Entity, using Home Assistant's native `RestoreEntity` mechanism, restores a previously-persisted state as the State Machine's initial state before any evaluation runs.

This restoration is performed through `StateMachine.restore_state()`, a method distinct from `transition_to()`. It exists exclusively for this startup use, sets the current state directly, and deliberately bypasses the transition validation defined in §4 - restoring a prior process's last state is not itself a demand-driven transition. `restore_state()` shall never be called after the first evaluation has run, and shall never be used as a substitute for `transition_to()` during normal operation.

---

# 7. Responsibilities

The State Machine SHALL:

- store the current state;
- validate transitions;
- expose the current state;
- reject invalid transitions.

The State Machine SHALL NOT:

- evaluate demand;
- select heating sources;
- communicate with Home Assistant;
- communicate with devices;
- execute thermostat logic;
- execute protection logic.

---

# 8. Source of Truth

This document is the only definition of the Smart Thermostat State Machine.

The implementation shall strictly follow this specification.