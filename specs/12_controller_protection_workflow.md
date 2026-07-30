# Smart Thermostat

## Thermostat Controller Protection Workflow

Version: 2.0

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

1. Minimum Runtime

If the minimum runtime has not yet elapsed:

Remain in STOPPING.

If the minimum runtime has elapsed:

Continue.

2. Shutdown Delay - Climate Device only

Shutdown Delay SHALL be evaluated only while the Climate Device is the active heating
or cooling solution:

- Cooling (always performed by the Climate Device);
- Heating while the Climate Device is the active heating source.

Shutdown Delay SHALL NOT be evaluated while the Boiler is the active heating source. In
this case it is treated as immediately satisfied, and the transition to IDLE depends
only on Minimum Runtime.

If Shutdown Delay applies and has not yet expired:

Remain in STOPPING.

If Shutdown Delay applies and has expired, or does not apply:

The transition to IDLE is allowed.

Only after the transition to IDLE has been completed may the Thermostat Controller request the active device to stop.

### Rationale for the Boiler exception

Radiator-based Boiler heating already has significant thermal inertia. Keeping the
Boiler active after thermal demand has disappeared would continue injecting heat into
the system and cause unnecessary overshoot. Shutdown Delay therefore remains beneficial
for the Climate Device (compressor cycling protection) but is intentionally not applied
to the Boiler.

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

1. Minimum Runtime

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

1. Minimum Runtime
2. Shutdown Delay (Climate Device only - see §3)

For heating source changes:

1. Minimum Runtime
2. Source Change Delay

The evaluation order is fixed.

Minimum Runtime is the same protection, and the same configured value, in both cases -
it always answers the same question: has the currently active heating or cooling
solution been active for long enough to be stopped or replaced.

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