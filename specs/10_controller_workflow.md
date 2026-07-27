# Smart Thermostat

## Thermostat Controller Workflow

Version: 2.0

Status: Frozen

---

# 1. Purpose

This document defines the execution workflow of the Thermostat Controller.

The Thermostat Controller is the orchestration component of the Smart Thermostat domain.

It coordinates the execution of the domain components.

It contains no business logic.

Every decision is delegated to a specialized component.

---

# 2. Responsibilities

The Thermostat Controller SHALL:

- receive a Runtime Context;
- orchestrate the complete evaluation workflow;
- invoke the appropriate domain components;
- update the State Machine;
- update the Thermostat Runtime State;
- request device actions;
- produce the evaluation result.

The Thermostat Controller SHALL NOT:

- read Home Assistant entities;
- read Config Entry values;
- evaluate thermal demand;
- evaluate transition rules;
- evaluate protection rules;
- evaluate heating source selection.

---

# 3. Input

The Thermostat Controller receives exactly one input.

- Runtime Context

The Runtime Context contains every runtime value required for one evaluation cycle.

---

# 4. Evaluation Workflow

For every evaluation cycle the Thermostat Controller SHALL execute the following sequence.

---

## Step 1

Receive the Runtime Context.

---

## Step 2

Invoke the Demand Engine.

Input:

- Runtime Context

Output:

- NO_DEMAND
- HEATING
- COOLING

---

## Step 3

If the demand is HEATING:

Invoke the Source Engine.

Input:

- Runtime Context

Output:

- BOILER
- AIR_CONDITIONER

If the demand is not HEATING:

No heating source evaluation is performed.

---

## Step 4

Invoke the Transition Table.

Inputs:

- Current Thermostat State
- Current Demand

Output:

- Requested Thermostat State

The Thermostat Controller never derives transition rules.

---

## Step 5

If a state transition or heating source change requires protection:

Invoke the Protection Engine.

Input:

- Runtime Context

Output:

- ALLOWED
- DENIED

The Thermostat Controller never evaluates protection rules.

---

## Step 6

If the requested transition is authorized:

Update the State Machine.

If authorization is denied:

Keep the current logical state.

---

## Step 7

Update the Thermostat Runtime State.

The Thermostat Controller SHALL update every persistent runtime field whose value changed during the evaluation.

Typical updates include:

- Current Heating Source
- Device Started At
- Demand Ended At
- Source Selected At
- Desired Source Differs Since

The Thermostat Runtime State shall always represent the current persistent runtime information after the evaluation completes.

---

## Step 8

Generate the Thermostat Controller Result.

The result SHALL contain only the information required by the Home Assistant integration layer.

---

# 5. Workflow Principles

The Thermostat Controller is an orchestrator.

Every decision is delegated.

Every persistent runtime update is centralized.

The Thermostat Controller is the only component allowed to modify the Thermostat Runtime State.

---

# 6. Error Handling

If any domain component raises an exception:

- terminate the current evaluation;
- do not update the State Machine;
- do not update the Thermostat Runtime State;
- do not execute device commands.

Exception handling outside the domain layer is the responsibility of the Home Assistant integration.

---

# 7. Source of Truth

This document defines the complete execution workflow of the Thermostat Controller.

Every implementation shall strictly follow this workflow.