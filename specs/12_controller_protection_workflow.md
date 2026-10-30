# Smart Thermostat

## Thermostat Controller Protection Workflow

Version: 2.3

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

1. Minimum Runtime - Climate Device only

Minimum Runtime SHALL be evaluated only while the Climate Device is the active heating
or cooling solution:

- Cooling (always performed by the Climate Device);
- Heating while the Climate Device is the active heating source.

Minimum Runtime SHALL NOT be evaluated while the Boiler is the active heating source. In
this case it is treated as immediately satisfied.

If Minimum Runtime applies and has not yet elapsed:

Remain in STOPPING.

If Minimum Runtime applies and has elapsed, or does not apply:

Continue.

2. Shutdown Delay - Climate Device only, automatic shutdown only

Shutdown Delay SHALL be evaluated only when both of the following are true:

- the Climate Device is the active heating or cooling solution (Cooling, which is
  always performed by the Climate Device, or Heating while the Climate Device is the
  active heating source);
- the shutdown is an automatic consequence of thermal demand ending, i.e. the
  thermostat remains enabled (specs/21_external_state_transitions.md §4).

Shutdown Delay SHALL NOT be evaluated:

- while the Boiler is the active heating source, regardless of why the shutdown is
  occurring;
- when the shutdown was caused by an explicit user request to turn the thermostat OFF,
  regardless of which source is active.

In either case it is treated as immediately satisfied, and the transition to IDLE
depends only on Minimum Runtime.

If Shutdown Delay applies and has not yet expired:

Remain in STOPPING.

If Shutdown Delay applies and has expired, or does not apply:

The transition to IDLE is allowed.

Only after the transition to IDLE has been completed may the Thermostat Controller request the active device to stop.

### Rationale for the Boiler exception

Radiator-based Boiler heating already has significant thermal inertia. Keeping the
Boiler active after thermal demand has disappeared would continue injecting heat into
the system and cause unnecessary overshoot. Neither Minimum Runtime nor Shutdown Delay
therefore ever apply to the Boiler: it stops immediately once no other applicable
condition blocks it. Both protections remain beneficial for the Climate Device
(compressor cycling protection), which is the only device they were ever intended to
protect.

### Rationale for the explicit-OFF exception

Shutdown Delay exists to smooth out automatic shutdowns that happen while the
thermostat is still enabled and demand has merely ended - not to delay a shutdown the
user explicitly requested. When the user turns the thermostat OFF, the only protection
that may still delay the physical shutdown is Minimum Runtime, and only for the Climate
Device. See § "USER-REQUESTED OFF vs AUTOMATIC DEMAND TERMINATION" below.

---

## STARTING → IDLE

If the demand that caused STARTING disappears before HEATING/COOLING is confirmed, the
requested state becomes IDLE (specs/11_controller_transition_table.md §7).

This transition SHALL use exactly the same protection model as STOPPING → IDLE above:
the same Minimum Runtime check (Climate Device only), the same Shutdown Delay check
(Climate Device only, automatic shutdown only - never for an explicit user OFF request),
and the same Boiler exemption from both.

This is deliberately not the same treatment as STOPPING → STARTING. STOPPING → STARTING
is unconditional and ungated because the controlled device was never told to stop -
there is nothing pending for either protection to guard. STARTING → IDLE is different:
the Requested Device Actions that activate the controlled device (specs/17_requested_
device_actions.md) are generated the moment STARTING is entered (IDLE → STARTING), so by
the time demand disappears the Climate Device may already be physically running. The
same protections that guard against stopping it too soon after a completed episode
(STOPPING → IDLE) apply identically to guard against stopping it too soon after a
startup that is cancelled almost immediately.

Only after the transition to IDLE has been completed may the Thermostat Controller
request the active device to stop.

The USER-REQUESTED OFF vs AUTOMATIC DEMAND TERMINATION distinction below applies to
STARTING → IDLE exactly as it applies to STOPPING → IDLE.

---

## STOPPING → STARTING

If demand returns while the thermostat is still STOPPING - before the STOPPING → IDLE
protection checks above have allowed the shutdown to complete - the requested state
becomes STARTING (specs/11_controller_transition_table.md §8).

No protection check applies to this transition.

Neither Minimum Runtime nor Shutdown Delay evaluate this transition. Minimum Runtime and
Shutdown Delay both exist to control when the controlled device is actually told to
stop; while STOPPING, the device has not yet been told to stop (it is only requested to
stop once IDLE is reached), so there is nothing pending for either protection to guard.
The pending shutdown is simply cancelled.

This transition SHALL be evaluated immediately, in the same evaluation cycle in which the
new demand is observed, and SHALL NOT be delayed to wait out any remaining Shutdown Delay
or Minimum Runtime window.

This transition SHALL NOT reset any runtime timer that assumes the controlled device
physically stopped and restarted (in particular, Device Started At - see
specs/15_runtime_state_update_rules.md §5). The device was never told to stop, so its
existing runtime timers remain valid and SHALL be preserved unchanged.

---

## USER-REQUESTED OFF vs AUTOMATIC DEMAND TERMINATION

Every shutdown reaching STOPPING → IDLE or STARTING → IDLE is caused by one of two
distinct events, and this document draws a strict distinction between them:

**Automatic demand termination**: the thermostat remains enabled, but thermal demand
has ended (the room has reached its target temperature). Normal shutdown protection
applies:

- Climate Device: Minimum Runtime, then Shutdown Delay.
- Boiler: neither protection applies - immediate shutdown.

**Explicit user OFF**: the user has changed the Home Assistant HVAC Mode to OFF
(specs/21_external_state_transitions.md §3/§4). Shutdown Delay SHALL NOT apply, for
either device:

- Climate Device: Minimum Runtime is the only protection that may still delay the
  shutdown.
- Boiler: neither protection applies - immediate shutdown, exactly as for automatic
  termination.

These two events SHALL NOT share identical shutdown-protection semantics: an explicit
user OFF request always bypasses Shutdown Delay, even while the Climate Device is
active, whereas an automatic demand termination while the Climate Device is active is
always subject to it.

The Thermostat Controller distinguishes the two using the same `enabled` input it
already receives from the Climate Entity for every evaluation
(specs/21_external_state_transitions.md): `enabled = False` means the user has
requested OFF; `enabled = True` with no demand means an automatic termination. No
additional state or signal is introduced to make this distinction.

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

1. Minimum Runtime - Climate Device only

Minimum Runtime SHALL be evaluated only when the *current* (about to be replaced)
heating source is the Climate Device. It SHALL NOT be evaluated when the current
heating source is the Boiler - in this case it is treated as immediately satisfied, and
the Boiler is never blocked from being replaced by the other source.

If Minimum Runtime applies and is denied:

The current heating source remains active.

If Minimum Runtime applies and is allowed, or does not apply:

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

1. Minimum Runtime (Climate Device only - see §3)
2. Shutdown Delay (Climate Device only, automatic shutdown only - see §3)

For heating source changes:

1. Minimum Runtime (Climate Device only - see §4)
2. Source Change Delay

The evaluation order is fixed.

Minimum Runtime is the same protection, and the same configured value, in both cases -
it always answers the same question: has the Climate Device been active for long enough
to be stopped or replaced. It uses the same underlying timestamp (Device Started At) and
the same configured duration whether the check is triggered by a shutdown or by a
source change. It is never evaluated at all when the Climate Device is not the device
being stopped or replaced - the Boiler is unconditionally exempt from Minimum Runtime,
in every context.

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