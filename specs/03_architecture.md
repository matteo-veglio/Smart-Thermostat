# Smart Thermostat

## Software Architecture

Version: 1.0

Status: Frozen

---

# 1. Purpose

This document defines the software architecture of the Smart Thermostat integration.

The architecture defines the responsibilities of every software component.

Implementation details are intentionally excluded.

---

# 2. Architecture Principles

The architecture follows the following principles.

## Single Responsibility

Every component has exactly one responsibility.

No component shall perform multiple independent tasks.

---

## Loose Coupling

Components communicate only through clearly defined interfaces.

A component shall never directly access the internal implementation of another component.

---

## High Cohesion

All functionality belonging to the same responsibility shall be implemented inside the same component.

---

## Deterministic Behaviour

Given the same inputs and the same internal state, every component shall always produce the same output.

---

## Testability

Every component shall be independently testable.

---

# 3. High Level Architecture

The integration is divided into independent logical components.

```
                     Climate Entity
                           │
                           ▼
                Thermostat Controller
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
 Demand Engine      Source Engine     Protection Engine
                           │
                           ▼
                     State Machine
                           │
                           ▼
                    Device Controller
                     ┌──────────────┐
                     ▼              ▼
          Boiler Controller   Climate Controller
```

---

# 4. Component Responsibilities

## Climate Entity

Responsibilities

- Expose the thermostat to Home Assistant.
- Expose the entity state.
- Receive user commands.
- Expose target temperatures.
- Expose presets.
- Expose HVAC mode.
- Expose HVAC action.

The Climate Entity shall never implement business logic.

---

## Thermostat Controller

Responsibilities

- Execute the control cycle.
- Coordinate every software component.
- Read all inputs.
- Collect every decision.
- Execute the resulting transition.
- Update the Climate Entity.

The Thermostat Controller is the orchestrator of the entire integration.

---

## Demand Engine

Responsibilities

- Evaluate indoor temperature.
- Evaluate thermostat tolerance.
- Determine thermal demand.

Possible outputs

- No Demand
- Heating Required
- Cooling Required

The Demand Engine never knows which physical devices are available.

---

## Source Engine

Responsibilities

- Determine the desired heating source.
- Evaluate photovoltaic surplus.
- Evaluate the configured energy policy.

Possible outputs

- Boiler
- Air Conditioner

The Source Engine never controls physical devices.

It only determines the desired source.

---

## Protection Engine

Responsibilities

- Evaluate every protection rule.
- Authorize or deny state transitions.
- Authorize or deny device operations.

Protection rules include

- minimum runtime;
- minimum source runtime;
- source change delay;
- shutdown delay.

The Protection Engine never decides what should happen.

It only decides whether an operation is currently allowed.

---

## State Machine

Responsibilities

- Maintain the current operating state.
- Validate every state transition.
- Determine the next operating state.

The State Machine never evaluates thermal demand.

The State Machine never evaluates protection rules.

---

## Device Controller

Responsibilities

- Generate Home Assistant service calls.
- Dispatch commands to the appropriate controller.

The Device Controller contains no decision logic.

---

## Boiler Controller

Responsibilities

- Start the boiler.
- Stop the boiler.

The Boiler Controller simply executes commands.

---

## Climate Controller

Responsibilities

- Set HVAC mode.
- Set HVAC target temperature.
- Turn the HVAC on.
- Turn the HVAC off.

The Climate Controller never determines the requested temperature.

It only executes commands received from the Device Controller.

---

# 5. Control Flow

Every control cycle shall execute the following sequence.

1. Read Inputs

2. Evaluate Thermal Demand

3. Determine Desired Source

4. Evaluate Protection Rules

5. Execute State Machine

6. Generate Device Commands

7. Update Climate Entity

The execution order shall never change.

---

# 6. Information Ownership

Every information item has exactly one owner.

## Demand Engine

Owns

- Thermal Demand

---

## Source Engine

Owns

- Desired Source

---

## Protection Engine

Owns

- Operation Authorization

---

## State Machine

Owns

- Current State

---

## Device Controller

Owns

- Device Commands

---

## Climate Entity

Owns

- Entity State
- HVAC Mode
- HVAC Action
- Target Temperatures
- Preset

No information shall have multiple owners.

---

# 7. Allowed Dependencies

The following dependency graph is allowed.

Climate Entity

↓

Thermostat Controller

↓

Demand Engine

↓

Source Engine

↓

Protection Engine

↓

State Machine

↓

Device Controller

↓

Boiler Controller

↓

Climate Controller

Reverse dependencies are forbidden.

Circular dependencies are forbidden.

---

# 8. Architectural Constraints

The architecture shall never allow

- duplicated business logic;
- duplicated protection logic;
- duplicated temperature calculations;
- direct device access from the Climate Entity;
- circular dependencies;
- hidden operating states.

Every responsibility shall belong to exactly one component.

---

# 9. Extensibility

Future versions may introduce additional controllers.

Examples include

- Heat Pump Controller
- Fan Controller
- Dehumidifier Controller

New controllers shall integrate through the Device Controller.

Existing component responsibilities shall remain unchanged.

---

# 10. Source of Truth

This document is the authoritative definition of the Smart Thermostat software architecture.

Component responsibilities defined in this document shall never be duplicated elsewhere.

Any architectural modification requires an explicit update of this document.