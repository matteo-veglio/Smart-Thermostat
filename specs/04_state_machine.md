# Smart Thermostat

## State Machine

Version: 2.0

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
| HEATING | STOPPING |
| COOLING | STOPPING |
| STOPPING | IDLE |
| STOPPING | OFF |

Any transition not listed above shall be rejected.

---

# 5. Invalid Transitions

The State Machine shall reject every transition not explicitly defined in this document.

Invalid transitions shall generate an exception.

The State Machine shall never silently ignore invalid transitions.

---

# 6. State Persistence

The current state shall be stored internally by the State Machine.

No persistence to Home Assistant is performed by this component.

Persistence across Home Assistant restarts is the responsibility of higher-level components.

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