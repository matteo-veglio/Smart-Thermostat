# Smart Thermostat

## Thermostat Controller Workflow

Version: 2.3

Status: Frozen

---

# 1. Purpose

This document defines the complete evaluation workflow executed by the Thermostat Controller.

The Thermostat Controller is the only component responsible for evaluating the thermostat.

The workflow is deterministic.

Every evaluation shall always execute the same sequence of steps.

---

# 2. Responsibilities

The Thermostat Controller SHALL:

- receive a Runtime Context;
- evaluate thermal demand;
- select the heating source;
- evaluate all protection rules;
- determine the requested thermostat state;
- determine the requested operation;
- determine the requested climate device target temperature when required;
- generate the Requested Device Actions;
- update the Thermostat Runtime State;
- return a Thermostat Controller Result.

The Thermostat Controller SHALL NOT:

- communicate with Home Assistant;
- execute Home Assistant services;
- communicate with physical devices.

---

# 3. Workflow

The Thermostat Controller SHALL execute the following steps in order.

### Step 1

Receive the Runtime Context.

### Step 2

Evaluate the thermal demand.

### Step 3

Determine the desired heating source.

### Step 4

Evaluate all protection rules.

### Step 5

Determine the requested thermostat state.

### Step 6

Determine the Requested Operation.

The Requested Operation SHALL be derived exclusively from the Requested Thermostat State.

The Requested Operation SHALL be fully determined before any subsequent workflow step is executed.

### Step 7

If the Requested Operation requires a Climate Device target temperature, evaluate the Climate Control Table.

The Climate Control Table SHALL receive:

- Requested Operation;
- Current Room Temperature;
- User Heating Target Temperature;
- User Cooling Target Temperature.

The Climate Control Table SHALL return exactly one Climate Device target temperature.

If the Requested Operation does not require a Climate Device target temperature, this step shall be skipped.

### Step 8

Generate the Requested Device Actions.

The Requested Device Actions SHALL use:

- Requested Thermostat State;
- Requested Operation;
- Requested Climate Device Target Temperature (when available).

### Step 9

Update the Thermostat Runtime State.

### Step 10

Generate the Thermostat Controller Result.

The Thermostat Controller Result SHALL contain:

- Current Thermostat State;
- Requested Thermostat State;
- Current Heating Source;
- Requested Heating Source;
- Current Operation;
- Requested Operation;
- Protection Result;
- Requested Device Actions.

---

# 4. Requested Operation

The Requested Operation represents the operation that the thermostat intends to perform after the current evaluation.

It is derived exclusively from the Requested Thermostat State.

The Requested Operation SHALL NOT be derived by the Climate Control Table.

The Requested Operation SHALL NOT be derived by the Device Action Generation process.

The Requested Operation SHALL be determined exactly once during every evaluation cycle.

---

# 5. Climate Control Table

The Climate Control Table is part of the Thermostat Controller evaluation workflow.

It SHALL consume the Requested Operation.

It SHALL NOT determine the Requested Operation.

It SHALL only determine the requested Climate Device target temperature.

---

# 6. Requested Device Actions

Requested Device Actions SHALL be generated only after:

- the Requested Thermostat State has been determined;
- the Requested Operation has been determined;
- the Climate Device target temperature has been determined (when required).

The Requested Device Actions SHALL never perform additional domain evaluations.

---

# 7. Runtime State Update

The Thermostat Runtime State SHALL be updated only after all domain decisions have been completed.

The Runtime State update SHALL never influence the current evaluation cycle.

Its effects apply only to subsequent evaluations.

---

# 8. Result Generation

The Thermostat Controller Result is the only output produced by the Thermostat Controller.

It SHALL completely describe the outcome of the evaluation.

No additional domain information shall be required by downstream components.

---

# 9. Determinism

Given identical Runtime Context values and identical Thermostat Runtime State values, the Thermostat Controller SHALL always produce an identical Thermostat Controller Result.

---

# 10. Source of Truth

This document defines the complete evaluation workflow of the Thermostat Controller.

Every implementation shall strictly follow this specification.