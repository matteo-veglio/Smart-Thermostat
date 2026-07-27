# Smart Thermostat

## Thermostat Runtime State Update Rules

Version: 1.1

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

Updates occur only after the evaluation has completed successfully.

The Runtime Context is never modified.

The Runtime Context represents the input snapshot.

The Thermostat Runtime State represents the persistent state after the evaluation.

Updates are expressed in terms of domain events rather than specific State Machine transitions.

---

# 3. Current Heating Source

## Update

Update the Current Heating Source whenever a heating source change is authorized and becomes effective.

The new value SHALL be the newly active heating source.

## Preserve

Preserve the current value while the active heating source does not change.

## Reset

The Current Heating Source is never reset independently.

---

# 4. Device Started At

This timestamp records when the currently controlled heating or cooling device becomes operational.

## Update

Update the timestamp when:

- a heating device becomes active;
- a cooling device becomes active.

The value SHALL be the current monotonic time.

## Preserve

Preserve the timestamp while the same device continues operating.

## Reset

Reset the timestamp when no heating or cooling device remains active.

---

# 5. Demand Ended At

This timestamp records when thermal demand disappears.

## Update

Update the timestamp when thermal demand changes from an active demand to NO_DEMAND.

The value SHALL be the current monotonic time.

## Preserve

Preserve the timestamp while thermal demand remains absent.

## Reset

Reset the timestamp when a new heating or cooling demand begins.

---

# 6. Source Selected At

This timestamp records when the currently active heating source became active.

## Update

Update the timestamp whenever a heating source change becomes effective.

The value SHALL be the current monotonic time.

## Preserve

Preserve the timestamp while the same heating source remains active.

## Reset

This timestamp is never reset independently.

It changes only when another heating source becomes active.

---

# 7. Desired Source Differs Since

This timestamp records when the preferred heating source first became different from the currently active heating source.

## Update

If:

- Requested Heating Source ≠ Current Heating Source

and no timestamp is currently stored,

store the current monotonic time.

## Preserve

Preserve the timestamp while the requested heating source continues to differ from the active heating source.

## Reset

Reset the timestamp immediately when:

- Requested Heating Source = Current Heating Source.

---

# 8. Atomic Update

All Runtime State updates belonging to a single evaluation cycle SHALL be committed atomically.

Partial updates are not allowed.

If the evaluation fails, the Thermostat Runtime State SHALL remain unchanged.

---

# 9. Relationship with Protection Engine

The Protection Engine never updates the Thermostat Runtime State.

It only evaluates the existing runtime information.

The Thermostat Controller applies Runtime State updates after the evaluation has completed successfully.

---

# 10. Relationship with Runtime Context

The Runtime Context contains a snapshot of the Thermostat Runtime State taken before the evaluation begins.

The Runtime Context never reflects updates performed during the current evaluation.

Updated Runtime State values become visible only during the next evaluation cycle.

---

# 11. Source of Truth

This document defines the official update policy for the Thermostat Runtime State.

Every implementation shall strictly follow these rules.

No undocumented update behaviour shall ever be implemented.