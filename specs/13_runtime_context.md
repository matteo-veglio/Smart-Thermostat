# Smart Thermostat

## Runtime Context

Version: 1.0

Status: Frozen

---

# 1. Purpose

This document defines the Runtime Context used by the Thermostat Controller.

The Runtime Context is a read-only data object that contains every runtime value required to evaluate the thermostat.

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
- communicate with Home Assistant.

---

# 3. Runtime Context Factory

The Runtime Context is created by the Runtime Context Factory.

The Runtime Context Factory is responsible for collecting runtime information from:

- Home Assistant entities;
- Config Entry values;
- runtime state maintained by the integration.

The Runtime Context Factory performs no business logic.

Its only responsibility is assembling a complete Runtime Context.

---

# 4. Runtime Context Contents

The Runtime Context SHALL contain the following information.

## Thermostat State

- Current Thermostat State

---

## Heating Source

- Current Heating Source

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

## Protection Timing

- Current Monotonic Time
- Device Started At
- Demand Ended At
- Source Selected At
- Desired Source Differs Since

---

## Protection Configuration

- Minimum Device Runtime
- Minimum Source Runtime
- Shutdown Delay
- Source Change Delay

---

# 5. Evaluation Cycle

For every thermostat evaluation:

1. The Runtime Context Factory creates a new Runtime Context.
2. The Runtime Context is passed to the Thermostat Controller.
3. The Thermostat Controller evaluates the complete control workflow.
4. The Runtime Context is discarded.

A Runtime Context shall never be reused across evaluation cycles.

---

# 6. Immutability

The Runtime Context is immutable.

No component may modify its contents after creation.

If runtime information changes, a new Runtime Context shall be created.

---

# 7. Dependencies

The Runtime Context depends on no other domain component.

The following components consume the Runtime Context:

- Thermostat Controller

No other component shall require direct access to Home Assistant runtime data.

---

# 8. Design Principles

The Runtime Context is a Data Transfer Object (DTO).

Its purpose is transporting runtime data between the Home Assistant integration layer and the domain layer.

It intentionally contains:

- no behaviour;
- no calculations;
- no decision logic.

---

# 9. Source of Truth

This document defines the Runtime Context used by the Smart Thermostat.

Every implementation shall strictly follow this specification.