# Smart Thermostat

## Thermostat Runtime State

Version: 1.0

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
- be owned by the Thermostat Controller;
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
2. The Runtime Context includes the current Thermostat Runtime State.
3. The Thermostat Controller evaluates the Runtime Context.
4. The Thermostat Controller updates the Thermostat Runtime State if required.

---

# 4. Stored Information

The Thermostat Runtime State SHALL contain:

## Heating Source

- Current Heating Source

---

## Protection Timing

- Device Started At
- Demand Ended At
- Source Selected At
- Desired Source Differs Since

No additional runtime information shall be stored unless explicitly documented.

---

# 5. Ownership

The Thermostat Controller is the only component allowed to modify the Thermostat Runtime State.

All other components shall treat it as read-only.

The Runtime Context Factory may read it.

The Runtime Context may contain a copy of its values.

---

# 6. Update Policy

The Thermostat Runtime State is updated only after the Thermostat Controller has completed an evaluation.

It is never modified during Runtime Context creation.

It is never modified by Home Assistant components.

---

# 7. Immutability

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
- shared across evaluation cycles.

These responsibilities shall never be mixed.

---

# 9. Source of Truth

This document defines the Thermostat Runtime State used by the Smart Thermostat.

Every implementation shall strictly follow this specification.