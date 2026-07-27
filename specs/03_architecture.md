# Smart Thermostat

## Software Architecture

Version: 2.2

Status: Frozen

---

# 1. Architecture Overview

The Smart Thermostat is composed of independent software components.

Each component has a single responsibility.

Business logic is distributed across specialized engines.

The Thermostat Controller orchestrates the interaction between all components.

The Home Assistant integration layer is responsible for collecting runtime information and converting it into a Runtime Context.

---

# 2. Architecture

```
                    Home Assistant
                           │
                           ▼
                    Climate Entity
                           │
                           ▼
               Runtime Context Factory
                           │
                           ▼
                   Runtime Context
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
- exposing the current thermostat state;
- requesting thermostat evaluations.

It shall never contain thermostat logic.

---

## Runtime Context Factory

Responsible for:

- collecting runtime information from Home Assistant;
- reading Config Entry values;
- collecting runtime timestamps;
- creating a complete Runtime Context.

The Runtime Context Factory performs no business logic.

It only assembles runtime data.

---

## Runtime Context

Responsible only for transporting runtime information from the Home Assistant integration layer to the Thermostat Controller.

The Runtime Context:

- is immutable;
- contains no behaviour;
- contains no business logic;
- contains no Home Assistant objects.

---

## Thermostat Controller

Responsible for:

- orchestrating the complete thermostat operation;
- coordinating all internal engines;
- evaluating a Runtime Context;
- requesting thermal demand evaluation;
- requesting heating source selection;
- requesting protection evaluation;
- requesting state transitions;
- requesting device actions;
- producing the orchestration result.

The Thermostat Controller contains no business logic of its own.

It delegates every decision to the appropriate component.

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

- heating sources;
- photovoltaic surplus;
- timers;
- protection logic.

---

## Demand Engine

Responsible only for determining the current thermal demand.

Inputs:

- Runtime Context

Outputs:

- NO_DEMAND
- HEATING
- COOLING

The Demand Engine reads only the fields required for its evaluation.

It never selects the heating source.

---

## Source Engine

Responsible only for selecting the preferred heating source.

Inputs:

- Runtime Context

Outputs:

- BOILER
- AIR_CONDITIONER

The Source Engine reads only the fields required for its evaluation.

It never evaluates thermal demand.

---

## Protection Engine

Responsible only for evaluating timing constraints.

Inputs:

- Runtime Context

Outputs:

- ALLOWED
- DENIED

The Protection Engine reads only the fields required for its evaluation.

It never performs transitions.

---

## Device Controllers

Responsible only for communicating with physical devices through Home Assistant services.

Separate controllers exist for:

- Boiler
- Air Conditioner

They contain no business logic.

---

# 4. Information Flow

For every evaluation cycle:

1. The Climate Entity requests a thermostat evaluation.
2. The Runtime Context Factory creates a new Runtime Context.
3. The Runtime Context is passed to the Thermostat Controller.
4. The Thermostat Controller orchestrates all domain components.
5. The State Machine is updated if required.
6. Device Controllers execute the requested actions.
7. The Climate Entity updates its exposed state.

---

# 5. Design Principles

Every component has exactly one responsibility.

Business logic exists only inside the domain layer.

The Runtime Context separates the Home Assistant integration layer from the domain layer.

The Thermostat Controller is the only component allowed to coordinate multiple domain components.

No component shall duplicate another component's responsibility.

---

# 6. Source of Truth

This document defines the official software architecture of the Smart Thermostat.

Every implementation shall strictly follow this architecture.