# Smart Thermostat

## Thermostat Controller Protection Workflow

Version: 1.1

Status: Frozen

---

# 1. Purpose

This document defines how the Thermostat Controller interacts with the Protection Engine.

The Protection Engine never decides what should happen.

The Thermostat Controller never evaluates protection rules.

The Thermostat Controller is responsible only for requesting the appropriate protection checks before executing a state transition or changing the active heating source.

---

# 2. Principles

The Protection Engine evaluates only timing constraints.

It never:

- evaluates thermal demand;
- selects the heating source;
- changes the thermostat state;
- controls devices.

The Thermostat Controller decides which protection checks are required according to the requested operation.

---

# 3. State Transitions

## OFF → IDLE

No protection checks are required.

---

## IDLE → STARTING

No protection checks are required.

A startup request is always allowed.

---

## STARTING → HEATING

No protection checks are required.

The startup sequence has already been completed.

---

## STARTING → COOLING

No protection checks are required.

The startup sequence has already been completed.

---

## HEATING → STOPPING

No protection checks are required.

The transition to STOPPING represents the decision to terminate heating.

The currently active device continues operating while the shutdown sequence is in progress.

---

## COOLING → STOPPING

The same rules apply as for HEATING → STOPPING.

No protection checks are required.

The currently active device continues operating while the shutdown sequence is in progress.

---

## STOPPING → IDLE

Before leaving STOPPING, the Thermostat Controller SHALL verify:

1. Minimum Device Runtime

If the minimum runtime has not yet elapsed:

Remain in STOPPING.

If the minimum runtime has elapsed:

Continue.

2. Shutdown Delay

If the shutdown delay has not yet expired:

Remain in STOPPING.

If the shutdown delay has expired:

The transition to IDLE is allowed.

Only after the transition to IDLE has been completed may the Thermostat Controller request the active device to stop.

---

# 4. Heating Source Changes

Whenever the Thermostat Controller requests a change of heating source, it SHALL perform the following checks.

Required inputs:

- Current Heating Source
- Requested Heating Source

If both sources are identical:

No protection checks are required.

The current heating source remains unchanged.

If the requested source differs from the current source:

First evaluate:

1. Minimum Source Runtime

If denied:

The current heating source remains active.

If allowed:

Continue.

Then evaluate:

2. Source Change Delay

If denied:

The current heating source remains active.

If allowed:

The requested heating source becomes active.

---

# 5. Protection Evaluation Order

Whenever multiple protections are required, they SHALL always be evaluated in the following order.

For shutdown:

1. Minimum Device Runtime
2. Shutdown Delay

For heating source changes:

1. Minimum Source Runtime
2. Source Change Delay

The evaluation order is fixed.

---

# 6. Protection Result

Every protection check returns exactly one result.

Possible values:

- ALLOWED
- DENIED

The Thermostat Controller never evaluates timing values.

It only reacts to the Protection Engine result.

---

# 7. Responsibilities

## Thermostat Controller

Responsible for:

- determining which protection checks are required;
- invoking the Protection Engine;
- executing or rejecting the requested transition.

It never evaluates timing.

---

## Protection Engine

Responsible for:

- evaluating timing constraints;
- returning ALLOWED or DENIED.

It never performs transitions.

---

# 8. Source of Truth

This document defines the complete interaction between the Thermostat Controller and the Protection Engine.

Every implementation shall strictly follow this workflow.

No undocumented protection sequence shall ever be implemented.