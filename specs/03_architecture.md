# Smart Thermostat

## Software Architecture

Version: 2.3

Status: Frozen

---

# 1. Architecture Overview

The Smart Thermostat is composed of independent software components.

Each component has a single responsibility.

Business logic is distributed across specialized domain components.

The Home Assistant integration layer is responsible for collecting runtime information and translating it into a Runtime Context.

The domain layer is responsible for evaluating the thermostat behaviour and maintaining its persistent runtime state.

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
                           │
         ┌─────────────────┴─────────────────┐
         ▼                                   ▼
 Thermostat Runtime State             Domain Components
 (persistent state)              ┌────────┬────────┬────────┬────────┐
                                 ▼        ▼        ▼        ▼
                           State Machine Demand  Source  Protection
                                         Engine  Engine   Engine
                                                   │
                                                   ▼
                                           Transition Table
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
- requesting thermostat evaluations.

The Climate Entity shall never implement thermostat logic.

---

## Runtime Context Factory

Responsible for:

- collecting runtime information from Home Assistant;
- reading Config Entry values;
- reading the Thermostat Runtime State;
- assembling a Runtime Context.

The Runtime Context Factory performs no business logic.

---

## Runtime Context

Responsible only for transporting runtime information into the domain layer.

The Runtime Context:

- is immutable;
- exists only for one evaluation cycle;
- contains no behaviour;
- contains no business logic.

---

## Thermostat Controller

Responsible for:

- orchestrating the complete domain evaluation;
- coordinating every domain component;
- updating the Thermostat Runtime State;
- requesting device actions;
- producing the orchestration result.

The Thermostat Controller contains no business logic of its own.

---

## Thermostat Runtime State

Responsible for storing persistent runtime information.

The Thermostat Runtime State:

- survives between evaluation cycles;
- contains mutable runtime information;
- is owned exclusively by the Thermostat Controller.

No other component may modify it.

---

## State Machine

Responsible only for the logical operating state.

The State Machine stores only:

- OFF
- IDLE
- STARTING
- HEATING
- COOLING
- STOPPING

---

## Demand Engine

Responsible only for evaluating thermal demand.

Consumes Runtime Context.

Produces:

- NO_DEMAND
- HEATING
- COOLING

---

## Source Engine

Responsible only for selecting the preferred heating source.

Consumes Runtime Context.

Produces:

- BOILER
- AIR_CONDITIONER

---

## Protection Engine

Responsible only for evaluating timing constraints.

Consumes Runtime Context.

Produces:

- ALLOWED
- DENIED

---

## Transition Table

Responsible only for mapping:

- Current Thermostat State
- Current Demand

into:

- Requested Thermostat State

It performs no other operation.

---

## Device Controllers

Responsible only for communicating with Home Assistant services.

They execute commands.

They never make decisions.

---

# 4. Information Flow

For every evaluation cycle:

1. The Climate Entity requests a thermostat evaluation.
2. The Runtime Context Factory reads Home Assistant runtime data.
3. The Runtime Context Factory reads the Thermostat Runtime State.
4. The Runtime Context Factory creates a Runtime Context.
5. The Thermostat Controller evaluates the Runtime Context.
6. The Thermostat Controller updates the Thermostat Runtime State if necessary.
7. The State Machine is updated if required.
8. Device Controllers execute the requested actions.
9. The Climate Entity updates the Home Assistant entity state.

---

# 5. Design Principles

Every component has exactly one responsibility.

Persistent runtime information belongs exclusively to the Thermostat Runtime State.

Transient runtime information belongs exclusively to the Runtime Context.

The Runtime Context Factory is responsible only for assembling runtime information.

The Thermostat Controller is the only component allowed to modify the Thermostat Runtime State.

No component shall duplicate another component's responsibility.

---

# 6. Source of Truth

This document defines the official software architecture of the Smart Thermostat.

Every implementation shall strictly follow this architecture.