# Smart Thermostat

## Software Architecture

Version: 2.0

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
- updating the Climate Entity;
- dispatching commands to the Device Controllers.

The Thermostat Controller contains no decision logic of its own.

It delegates every decision to the appropriate engine.

---

## State Machine

Responsible only for the logical operating state of the thermostat.

It knows:

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

Responsible for determining the thermal demand.

Possible outputs:

- NO_DEMAND
- HEATING
- COOLING

It never selects the heating source.

---

## Source Engine

Responsible for selecting the heating source.

Possible outputs:

- NONE
- BOILER
- AIR_CONDITIONER

The decision is based on:

- instantaneous surplus;
- minimum surplus;
- protection constraints.

It never evaluates thermal demand.

---

## Protection Engine

Responsible for protecting the system.

It evaluates:

- shutdown delay;
- source change delay;
- minimum device runtime;
- minimum source runtime.

It never evaluates demand.

It never selects the source.

---

## Device Controllers

Responsible only for communicating with physical devices.

Separate controllers exist for:

- Boiler
- Air Conditioner

No decision logic exists inside Device Controllers.

---

# 4. Information Flow

The execution flow is:

1. Climate Entity receives a user command.
2. Thermostat Controller requests the current demand from the Demand Engine.
3. Demand Engine determines whether heating, cooling or no demand exists.
4. If heating is required, the Thermostat Controller asks the Source Engine to select the heating source.
5. The Protection Engine validates whether the requested transition is currently allowed.
6. The State Machine updates the logical operating state.
7. The Thermostat Controller dispatches commands to the appropriate Device Controller.
8. The Climate Entity is updated with the new state.

---

# 5. Design Principles

Every component shall have exactly one responsibility.

Components communicate only through well-defined interfaces.

No component shall duplicate another component's responsibility.

The State Machine shall never contain source selection logic.

The Source Engine shall never contain thermostat state logic.

---

# 6. Source of Truth

This document defines the official software architecture of the Smart Thermostat.

Every implementation shall strictly follow this architecture.