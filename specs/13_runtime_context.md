# Smart Thermostat

## Runtime Context

Version: 2.5

Status: Frozen

---

# 1. Purpose

This document defines the Runtime Context used by the Thermostat Controller.

The Runtime Context is an immutable snapshot containing every runtime value required to evaluate the thermostat during a single evaluation cycle.

It exists to decouple the domain layer from Home Assistant.

The Runtime Context contains data only.

It never contains business logic.

The Runtime Context represents only the inputs required for a thermostat evaluation.

The outputs of the evaluation are represented exclusively by the Thermostat Controller Result.

---

# 2. Responsibilities

The Runtime Context SHALL:

- contain every runtime input required by the Thermostat Controller;
- be immutable during a single evaluation cycle;
- contain no methods implementing business logic;
- be independent from Home Assistant.

The Runtime Context contains evaluation inputs only.

It never contains evaluation outputs.

Evaluation outputs are produced exclusively by the Thermostat Controller Result.

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
- Current Humidity (optional)

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
- Current Operation
- Device Started At
- Demand Ended At
- Source Selected At
- Desired Source Differs Since

The Runtime Context shall never modify these values.

---

## Device State Snapshot

The Runtime Context SHALL include a snapshot of the current physical state of every controlled device.

The Runtime Context Factory SHALL read the current device states from Home Assistant immediately before creating the Runtime Context.

The device state snapshot is the single source of truth for the current physical state of the controlled devices.

Initially the Runtime Context SHALL contain:

### Boiler

- Current Boiler Power State

### Climate Device

- Current Climate Power State
- Current Climate HVAC Mode
- Current Climate Target Temperature

Additional device state fields may be introduced when support for additional controlled devices is added.

The Runtime Context shall never modify these values.

The Thermostat Controller SHALL use the Device State Snapshot when determining the Requested Device Actions.

The Thermostat Runtime State SHALL NOT be used to infer the current physical state of controlled devices.

The Thermostat Runtime State contains only persistent domain information required across multiple evaluation cycles.

---

## Protection Configuration

- Current Monotonic Time
- Minimum Runtime
- Shutdown Delay
- Source Change Delay

---

## Optional Runtime Values

Some runtime values are optional.

If a runtime value is optional:

- it may be absent from the Runtime Context;
- domain components that do not require it shall ignore it.

Currently the following field is optional:

- Current Humidity

The absence of an optional runtime value shall never prevent a thermostat evaluation unless explicitly required by another specification.

---

## Values Never Contained in the Runtime Context

The Runtime Context never contains:

- HVAC Action;
- Requested Device Actions;
- Thermostat Controller Result;
- Device Controller state.

These values are produced only after the evaluation has completed.

---

# 5. Evaluation Cycle

For every thermostat evaluation:

1. The Runtime Context Factory reads Home Assistant data.
2. The Runtime Context Factory reads the current Thermostat Runtime State.
3. The Runtime Context Factory reads the current physical state of every controlled device.
4. The Runtime Context Factory creates a new Runtime Context.
5. The Runtime Context is passed to the Thermostat Controller.
6. The Thermostat Controller evaluates the Runtime Context.
7. The Thermostat Controller updates the Thermostat Runtime State if required.
8. The Thermostat Controller produces a Thermostat Controller Result.
9. The Runtime Context is discarded.

A Runtime Context shall never be reused across evaluation cycles.

---

# 6. Immutability

The Runtime Context is immutable.

No component may modify its contents after creation.

If runtime information changes, a new Runtime Context shall be created.

Persistent runtime information belongs exclusively to the Thermostat Runtime State.

Evaluation outputs belong exclusively to the Thermostat Controller Result.

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

The Runtime Context may contain optional runtime values.

Domain components shall read only the fields required for their own evaluation.

Components shall not require optional fields unless explicitly documented.

Persistent runtime information is managed separately by the Thermostat Runtime State.

The current physical state of controlled devices is managed separately through the Device State Snapshot.

Evaluation outputs are managed separately by the Thermostat Controller Result.

---

# 9. Source of Truth

This document defines the Runtime Context used by the Smart Thermostat.

Every implementation shall strictly follow this specification.