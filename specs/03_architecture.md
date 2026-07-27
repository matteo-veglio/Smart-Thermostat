# Smart Thermostat

## Software Architecture

Version: 2.1

Status: Frozen

---

# 1. Architecture Overview

The Smart Thermostat is composed of independent software components.

Each component has a single responsibility.

Business logic is distributed across specialized engines.

The Thermostat Controller orchestrates the interaction between all components.

---

# 2. Architecture

```
                Home Assistant
                       │
                       │
               Climate Entity
                       │
                       ▼
            Thermostat Controller
      ┌──────────┬──────────┬──────────┬──────────┐
      ▼          ▼          ▼          ▼
 State Machine Demand Engine Source Engine Protection Engine
      │
      ▼
 Device Controllers
      │
      ▼
 Boiler / Air Conditioner
```

---

# 3. Component Responsibilities

## Climate Entity

Responsible for:

- exposing the Home Assistant Climate interface;
- receiving user commands;
- exposing the current thermostat state.

It shall never contain thermostat logic.

---

## Thermostat Controller

Responsible for:

- orchestrating the complete thermostat operation;
- coordinating all internal engines;
- reading the current thermostat state;
- requesting thermal demand evaluation;
- requesting heating source selection;
- requesting protection evaluation;
- requesting state transitions;
- requesting device actions;
- producing the orchestration result.

The Thermostat Controller contains no business logic of its own.

It delegates every decision to the appropriate engine.

---

## State Machine

Responsible only for the logical operating state of the thermostat.

It knows only:

- OFF
- IDLE
- STARTING
- HEATING
- COOLING
- STOPPING

It never knows:

- which heating source is active;
- photovoltaic surplus;
- timers;
- protection logic.

---

## Demand Engine

Responsible only for determining the current thermal demand.

Inputs:

- current room temperature;
- heating target temperature;
- cooling target temperature;
- thermostat hysteresis;
- current thermostat state.

Outputs:

- NO_DEMAND
- HEATING
- COOLING

It never selects the heating source.

---

## Source Engine

Responsible only for selecting the preferred heating source.

Inputs:

- instantaneous energy surplus;
- minimum energy surplus.

Outputs:

- BOILER
- AIR_CONDITIONER.

It never evaluates thermal demand.

---

## Protection Engine

Responsible only for evaluating timing constraints.

It evaluates:

- shutdown delay;
- source change delay;
- minimum device runtime;
- minimum source runtime.

The Protection Engine never decides what should happen.

It only determines whether the requested operation is currently allowed.

Possible outputs:

- ALLOWED
- DENIED

---

## Device Controllers

Responsible only for communicating with physical devices.

Separate controllers exist for:

- Boiler
- Air Conditioner

No decision logic exists inside Device Controllers.

---

# 4. Information Flow

For every evaluation cycle:

1. The Thermostat Controller reads the current logical thermostat state.
2. The Demand Engine evaluates the current thermal demand.
3. If heating is required, the Source Engine selects the preferred heating source.
4. If a heating source change is required, the Thermostat Controller invokes the Protection Engine according to `specs/12_controller_protection_workflow.md`.
5. The Thermostat Controller determines the requested logical state according to `specs/11_controller_transition_table.md`.
6. If a state transition is required, the Thermostat Controller invokes the Protection Engine according to `specs/12_controller_protection_workflow.md`.
7. If authorized, the State Machine performs the requested transition.
8. The Thermostat Controller generates the orchestration result.
9. Device Controllers execute the requested actions.
10. The Climate Entity is updated.

---

# 5. Design Principles

Every component shall have exactly one responsibility.

Components communicate only through well-defined interfaces.

No component shall duplicate another component's responsibility.

The Thermostat Controller is the only component allowed to coordinate multiple engines.

The State Machine shall never contain source selection logic.

The Source Engine shall never contain thermostat state logic.

The Protection Engine shall never perform state transitions.

---

# 6. Source of Truth

This document defines the official software architecture of the Smart Thermostat.

Every implementation shall strictly follow this architecture.