# Smart Thermostat

## Thermostat Controller Transition Table

Version: 1.1

Status: Frozen

---

# 1. Purpose

This document defines how the Thermostat Controller determines the requested logical thermostat state.

The Thermostat Controller shall never derive transitions itself.

It shall strictly follow this table.

This table defines only the requested logical state.

Whether the transition is actually executed is determined later by the Protection Engine.

---

# 2. Inputs

The Thermostat Controller receives:

- Current Thermostat State
- Current Demand

Current Demand may be:

- NO_DEMAND
- HEATING
- COOLING

Current Thermostat State may be:

- OFF
- IDLE
- STARTING
- HEATING
- COOLING
- STOPPING

---

# 3. Transition Table

| Current State | Current Demand | Requested State | Notes |
|----------------|----------------|-----------------|-------|
| OFF | NO_DEMAND | OFF | Thermostat disabled. |
| OFF | HEATING | OFF | Thermostat must first be enabled by the user. |
| OFF | COOLING | OFF | Thermostat must first be enabled by the user. |
| IDLE | NO_DEMAND | IDLE | No action required. |
| IDLE | HEATING | STARTING | Begin heating startup sequence. |
| IDLE | COOLING | STARTING | Begin cooling startup sequence. |
| STARTING | NO_DEMAND | IDLE | Startup request cancelled before activation. |
| STARTING | HEATING | HEATING | Startup completed successfully. |
| STARTING | COOLING | COOLING | Startup completed successfully. |
| HEATING | NO_DEMAND | STOPPING | Begin shutdown sequence. |
| HEATING | HEATING | HEATING | Continue heating. |
| HEATING | COOLING | STOPPING | Heating must stop before cooling can begin. |
| COOLING | NO_DEMAND | STOPPING | Begin shutdown sequence. |
| COOLING | COOLING | COOLING | Continue cooling. |
| COOLING | HEATING | STOPPING | Cooling must stop before heating can begin. |
| STOPPING | NO_DEMAND | IDLE | Shutdown completed successfully. |
| STOPPING | HEATING | STARTING | Begin a new heating startup sequence. |
| STOPPING | COOLING | STARTING | Begin a new cooling startup sequence. |

---

# 4. Workflow

Every evaluation cycle follows these steps:

1. Read the current thermostat state.
2. Evaluate the current demand.
3. Determine the requested state using this table.
4. Request authorization from the Protection Engine.
5. If authorized, update the State Machine.
6. Return the orchestration result.

---

# 5. Design Principles

The Transition Table contains no business logic.

It is only a mapping between:

- Current State
- Current Demand
- Requested State

The table never:

- evaluates thermal demand;
- selects heating sources;
- evaluates protection rules;
- communicates with Home Assistant.

---

# 6. OFF State

The OFF state represents a disabled thermostat.

While the thermostat is OFF:

- the Demand Engine may still evaluate thermal demand;
- the Thermostat Controller ignores every heating or cooling request;
- the requested state always remains OFF.

Leaving the OFF state is possible only through an explicit user action.

---

# 7. STARTING State

STARTING is a real operating state.

It represents the period between:

- the authorization of a startup request; and
- the confirmation that the requested operating mode has become active.

The startup may include:

- device activation;
- HVAC mode changes;
- target temperature updates;
- any other initialization required before normal operation.

During STARTING the thermostat has already decided to begin heating or cooling, but the operating mode is not yet considered active.

If the startup request is cancelled before completion, the requested state becomes IDLE.

---

# 8. STOPPING State

STOPPING is a real operating state.

It represents the period between:

- the authorization of a shutdown request; and
- the completion of the shutdown sequence.

The shutdown may include:

- device shutdown;
- completion of shutdown delays;
- any other actions required before returning to the idle state.

During STOPPING the thermostat has already decided to stop heating or cooling, but the operating mode is not yet considered completed.

If a new demand appears during STOPPING, the requested state becomes STARTING.

Whether that transition is immediately allowed is determined exclusively by the Protection Engine.

---

# 9. Source of Truth

This document defines the complete transition policy of the Thermostat Controller.

The implementation shall strictly follow this table.

No undocumented transition shall ever be implemented.