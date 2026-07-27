# Smart Thermostat

## Thermostat Runtime State Update Rules

Version: 1.0

Status: Frozen

---

# 1. Purpose

This document defines how the Thermostat Runtime State is updated.

The Thermostat Runtime State contains persistent runtime information shared across evaluation cycles.

This document specifies exactly when every field is created, updated or reset.

No implementation shall infer update rules not explicitly documented here.

---

# 2. General Principles

The Thermostat Runtime State is updated only by the Thermostat Controller.

Updates occur only after the evaluation has completed.

The Runtime Context is never modified.

The Runtime Context represents the input snapshot.

The Thermostat Runtime State represents the persistent state after the evaluation.

---

# 3. Current Heating Source

## Update

The Current Heating Source SHALL be updated whenever the Thermostat Controller authorizes a heating source change.

The new value becomes the requested heating source.

## No Update

If the requested heating source is denied by the Protection Engine, the Current Heating Source remains unchanged.

---

# 4. Device Started At

This timestamp records when the currently active heating or cooling device started operating.

## Update

Update the timestamp when:

- the thermostat transitions from STARTING to HEATING;
- the thermostat transitions from STARTING to COOLING.

The value SHALL be the current monotonic time.

## Preserve

Keep the existing value while the same device continues operating.

## Reset

Reset the value when:

- the thermostat reaches IDLE;
- the thermostat transitions to OFF.

---

# 5. Demand Ended At

This timestamp records when thermal demand disappeared.

## Update

Update the timestamp when the Demand Engine changes from:

- HEATING → NO_DEMAND
- COOLING → NO_DEMAND

The value SHALL be the current monotonic time.

## Preserve

Keep the existing value while no new demand change occurs.

## Reset

Reset the value when a new heating or cooling demand begins.

---

# 6. Source Selected At

This timestamp records when the active heating source became active.

## Update

Update the timestamp whenever a heating source change is authorized.

The value SHALL be the current monotonic time.

## Preserve

Keep the existing value while the same heating source remains active.

## Reset

Never reset independently.

It changes only when a new source becomes active.

---

# 7. Desired Source Differs Since

This timestamp records when the preferred heating source first became different from the active heating source.

## Update

If:

Requested Heating Source ≠ Current Heating Source

and no timestamp is currently stored,

store the current monotonic time.

## Preserve

If the requested heating source remains different, preserve the original timestamp.

## Reset

Reset the timestamp immediately when:

Requested Heating Source = Current Heating Source.

---

# 8. Atomic Update

All Runtime State updates belonging to one evaluation cycle SHALL be committed together.

Partial updates are not allowed.

If the evaluation fails, the Thermostat Runtime State shall remain unchanged.

---

# 9. Relationship with Protection Engine

The Protection Engine never updates the Thermostat Runtime State.

It only evaluates the timestamps already stored.

The Thermostat Controller applies the updates after the evaluation has completed.

---

# 10. Relationship with Runtime Context

The Runtime Context contains a snapshot of the Thermostat Runtime State taken before the evaluation begins.

The Runtime Context never reflects updates performed during the current evaluation.

Updated values become visible only in the next evaluation cycle.

---

# 11. Source of Truth

This document defines the official update policy for the Thermostat Runtime State.

Every implementation shall strictly follow these rules.

No undocumented update behaviour shall ever be implemented.