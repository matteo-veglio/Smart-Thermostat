# Smart Thermostat

## Thermostat Runtime State

Version: 1.1

Status: Frozen

---

# 1. Purpose

This document defines the Thermostat Runtime State.

The Thermostat Runtime State contains all persistent runtime information required by the domain layer across multiple evaluation cycles.

Unlike the Runtime Context, the Thermostat Runtime State is persistent.

It survives between evaluations.

---

# 2. Responsibilities

The Thermostat Runtime State SHALL:

- store persistent runtime information;
- survive across evaluation cycles;
- be updated only by the Thermostat Controller.

The Thermostat Runtime State SHALL NOT:

- contain business logic;
- evaluate thermal demand;
- evaluate protection rules;
- communicate with Home Assistant.

---

# 3. Relationship with Runtime Context

The Runtime Context is a snapshot.

It is created for every evaluation cycle.

It is discarded after the evaluation completes.

The Thermostat Runtime State is persistent.

For every evaluation:

1. The Runtime Context Factory reads the current Thermostat Runtime State.
2. The Runtime Context includes a snapshot of the Thermostat Runtime State.
3. The Thermostat Controller evaluates the Runtime Context.
4. The Thermostat Controller updates the Thermostat Runtime State if required.

---

# 4. Stored Information

The Thermostat Runtime State SHALL contain the following information.

## Current Heating Source

The heating source currently selected by the thermostat.

Possible values:

- Boiler
- Air Conditioner

---

## Current Operation

The physical operation currently being performed by the thermostat.

Possible values:

- NONE
- HEATING
- COOLING

Current Operation is persistent.

It represents the physical operation that remains active across multiple evaluation cycles.

It SHALL be preserved until a domain event explicitly changes it.

---

## Protection Timing

The Thermostat Runtime State SHALL contain the following timestamps:

- Device Started At
- Demand Ended At
- Source Selected At
- Desired Source Differs Since

---

No additional runtime information shall be stored unless explicitly documented.

---

# 5. Ownership

The Thermostat Runtime State instance is owned by the Smart Thermostat integration.

The Thermostat Controller is the only component authorized to modify its contents.

All other components shall treat the Thermostat Runtime State as read-only.

The Runtime Context Factory may read it.

The Runtime Context contains only a snapshot of its current values.

---

# 6. Update Policy

The Thermostat Runtime State is updated only after the Thermostat Controller has completed an evaluation successfully.

It is never modified during Runtime Context creation.

It is never modified by Home Assistant components.

Every update SHALL follow:

- specs/15_runtime_state_update_rules.md

---

# 7. Mutability

The Thermostat Runtime State is mutable.

Its values change only when the Thermostat Controller updates them.

The Runtime Context remains immutable.

---

# 8. Design Principles

The Runtime Context and the Thermostat Runtime State have different responsibilities.

Runtime Context:

- immutable;
- evaluation input;
- discarded after every evaluation.

Thermostat Runtime State:

- persistent;
- mutable;
- shared across evaluation cycles;
- single source of truth for persistent runtime information.

These responsibilities shall never be mixed.

---

# 9. Source of Truth

This document defines the Thermostat Runtime State used by the Smart Thermostat.

Every implementation shall strictly follow this specification.