# Smart Thermostat

## Runtime Context

Version: 2.0

Status: Frozen

---

# 1. Purpose

This document defines the Runtime Context used by the Thermostat Controller.

The Runtime Context is an immutable snapshot containing every runtime value required to evaluate the thermostat during a single evaluation cycle.

It exists to decouple the domain layer from Home Assistant.

The Runtime Context contains data only.

It never contains business logic.

---

# 2. Responsibilities

The Runtime Context SHALL:

- contain every runtime input required by the Thermostat Controller;
- be immutable during a single evaluation cycle;
- contain no methods implementing business logic;
- be independent from Home Assistant.

The Runtime Context SHALL NOT:

- evaluate thermal demand;
- evaluate transition rules;
- evaluate protection rules;
- select heating sources;
- communicate with Home Assistant;
- own persistent runtime information.

---

# 3. Runtime Context Factory

The Runtime Context is created by the Runtime Context Factory.

The Runtime Context Factory is responsible for collecting runtime information from:

- Home Assistant entities;
- Config Entry values;
- the Thermostat Runtime State.

The Runtime Context Factory performs no business logic.

Its only responsibility is assembling a complete Runtime Context.

---

# 4. Runtime Context Contents

The Runtime Context SHALL contain the following information.

## Thermostat State

- Current Thermostat State

---

## Environment

- Current Room Temperature
- Current Humidity

---

## User Configuration

- Heating Target Temperature
- Cooling Target Temperature
- Thermostat Hysteresis

---

## Energy

- Instantaneous Energy Surplus
- Minimum Energy Surplus

---

## Runtime State Snapshot

The Runtime Context SHALL include a snapshot of the current Thermostat Runtime State.

This snapshot contains:

- Current Heating Source
- Device Started At
- Demand Ended At
- Source Selected At
- Desired Source Differs Since

The Runtime Context shall never modify these values.

---

## Protection Configuration

- Current Monotonic Time
- Minimum Device Runtime
- Minimum Source Runtime
- Shutdown Delay
- Source Change Delay

---

# 5. Evaluation Cycle

For every thermostat evaluation:

1. The Runtime Context Factory reads Home Assistant data.
2. The Runtime Context Factory reads the current Thermostat Runtime State.
3. The Runtime Context Factory creates a new Runtime Context.
4. The Runtime Context is passed to the Thermostat Controller.
5. The Thermostat Controller evaluates the Runtime Context.
6. The Thermostat Controller updates the Thermostat Runtime State if required.
7. The Runtime Context is discarded.

A Runtime Context shall never be reused across evaluation cycles.

---

# 6. Immutability

The Runtime Context is immutable.

No component may modify its contents after creation.

If runtime information changes, a new Runtime Context shall be created.

Persistent runtime information belongs exclusively to the Thermostat Runtime State.

---

# 7. Dependencies

The Runtime Context depends on no domain component.

The Runtime Context Factory may read:

- Home Assistant
- Config Entry
- Thermostat Runtime State

The following domain component consumes the Runtime Context:

- Thermostat Controller

No other domain component shall retrieve information directly from Home Assistant.

---

# 8. Design Principles

The Runtime Context is a Data Transfer Object (DTO).

Its purpose is transporting all runtime information required for a single evaluation cycle.

The Runtime Context intentionally contains:

- no behaviour;
- no calculations;
- no decision logic;
- no mutable runtime state.

Persistent runtime information is managed separately by the Thermostat Runtime State.

---

# 9. Source of Truth

This document defines the Runtime Context used by the Smart Thermostat.

Every implementation shall strictly follow this specification.