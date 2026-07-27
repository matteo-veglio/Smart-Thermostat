# Smart Thermostat

## Software Architecture

Version: 2.4

Status: Frozen

---

# 1. Architecture Overview

The Smart Thermostat is composed of independent software components.

Each component has a single responsibility.

Business logic is distributed across specialized domain components.

The Home Assistant integration layer is responsible for collecting runtime information and translating it into a Runtime Context.

The domain layer is responsible for evaluating the thermostat behaviour, maintaining its persistent runtime state and producing the Thermostat Controller Result.

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
        ┌──────────────────┴──────────────────┐
        ▼                                     ▼
Thermostat Runtime State          Thermostat Controller Result
 (persistent state)                     (evaluation output)
        │
        ▼
 ┌──────────────┬──────────────┬──────────────┬─────────────────┐
 ▼              ▼              ▼              ▼
State Machine Demand Engine Source Engine Protection Engine
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
- collecting runtime information;
- requesting thermostat evaluations;
- translating the Thermostat Controller Result into Home Assistant attributes.

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
- contains no business logic;
- contains only evaluation inputs.

---

## Thermostat Controller

Responsible for:

- orchestrating the complete domain evaluation;
- coordinating every domain component;
- updating the State Machine;
- updating the Thermostat Runtime State;
- determining the Current Operation;
- requesting device actions;
- producing the Thermostat Controller Result.

The Thermostat Controller contains no business logic of its own.

---

## Thermostat Controller Result

Responsible for exposing the evaluation outputs required by the Home Assistant integration.

It contains evaluation outputs only.

Typical information includes:

- Current Thermostat State;
- Current Operation;
- Current Heating Source;
- Requested Device Actions.

The Thermostat Controller Result is immutable.

---

## Thermostat Runtime State

Responsible for storing persistent runtime information.

The Thermostat Runtime State:

- survives between evaluation cycles;
- contains mutable runtime information;
- is owned by the integration;
- is modified exclusively by the Thermostat Controller.

---

## State Machine

Responsible only for maintaining the logical thermostat state.

Possible logical states are:

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

1. The Climate Entity collects runtime information.
2. The Runtime Context Factory reads Home Assistant runtime data.
3. The Runtime Context Factory reads the Thermostat Runtime State.
4. The Runtime Context Factory creates a Runtime Context.
5. The Thermostat Controller evaluates the Runtime Context.
6. The Thermostat Controller updates the Thermostat Runtime State if necessary.
7. The Thermostat Controller produces a Thermostat Controller Result.
8. The Climate Entity updates its Home Assistant state from the Thermostat Controller Result.
9. Device Controllers execute the requested actions when required.

---

# 5. Design Principles

Every component has exactly one responsibility.

Persistent runtime information belongs exclusively to the Thermostat Runtime State.

Transient runtime information belongs exclusively to the Runtime Context.

Evaluation outputs belong exclusively to the Thermostat Controller Result.

The Runtime Context Factory is responsible only for assembling runtime information.

The Thermostat Controller is the only component allowed to modify the Thermostat Runtime State.

The Climate Entity never derives thermostat behaviour.

No component shall duplicate another component's responsibility.

---

# 6. Source of Truth

This document defines the official software architecture of the Smart Thermostat.

Every implementation shall strictly follow this architecture.