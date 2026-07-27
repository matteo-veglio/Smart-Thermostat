# Smart Thermostat

## Thermostat Controller Workflow

Version: 1.1

Status: Frozen

---

# 1. Purpose

This document defines the execution workflow of the Thermostat Controller.

The Thermostat Controller is responsible only for orchestrating the internal components.

It never implements business logic.

Every decision is delegated to a specialized engine.

---

# 2. Responsibilities

The Thermostat Controller SHALL:

- coordinate the execution flow;
- invoke the appropriate engines;
- request state transitions;
- request device actions;
- expose the final result to the Home Assistant integration.

The Thermostat Controller SHALL NOT:

- evaluate thermal demand;
- select the heating source;
- evaluate protection rules;
- implement thermostat algorithms;
- communicate directly with physical devices.

---

# 3. Controller Inputs

The Thermostat Controller receives the following information for every evaluation cycle.

Thermostat state:

- Current Thermostat State

Environment:

- Current Room Temperature
- Current Humidity

Configuration:

- Heating Target Temperature
- Cooling Target Temperature
- Thermostat Hysteresis
- Minimum Energy Surplus

Energy:

- Instantaneous Energy Surplus

Heating Source:

- Current Heating Source

Timing Information:

- Current Monotonic Time
- Protection timestamps required by the Protection Engine

---

# 4. Execution Workflow

For every evaluation cycle, the Thermostat Controller SHALL execute the following steps.

---

## Step 1

Read the current logical thermostat state from the State Machine.

---

## Step 2

Evaluate the current thermal demand by invoking the Demand Engine.

Inputs:

- Current Room Temperature
- Heating Target Temperature
- Cooling Target Temperature
- Thermostat Hysteresis
- Current Thermostat State

Output:

- NO_DEMAND
- HEATING
- COOLING

---

## Step 3

If the Demand Engine returns HEATING:

Request the preferred heating source from the Source Engine.

Inputs:

- Instantaneous Energy Surplus
- Minimum Energy Surplus

Output:

- BOILER
- AIR_CONDITIONER

If the requested heating source differs from the current heating source:

The Thermostat Controller SHALL execute the protection workflow defined in:

specs/12_controller_protection_workflow.md

If the Demand Engine returns COOLING:

The configured Cooling Source is used.

If the Demand Engine returns NO_DEMAND:

No source selection is performed.

---

## Step 4

Determine the requested logical thermostat state.

The requested state SHALL be determined exclusively according to:

specs/11_controller_transition_table.md

The Thermostat Controller shall never derive transition rules itself.

---

## Step 5

If the requested logical state differs from the current logical state:

Execute the protection workflow defined in:

specs/12_controller_protection_workflow.md

If the Protection Engine returns DENIED:

The current logical state remains unchanged.

If the Protection Engine returns ALLOWED:

Update the State Machine.

---

## Step 6

Generate the orchestration result.

The result SHALL contain only:

- Current Demand
- Current Heating Source
- Requested Heating Source (if applicable)
- Current Thermostat State
- Requested Thermostat State
- Protection Result

The result SHALL NOT contain:

- Home Assistant entities
- Device objects
- Service calls
- Home Assistant types

---

# 5. Workflow Principles

The Thermostat Controller is an orchestrator.

It never makes decisions.

Every decision is delegated to one of the following components.

| Component | Responsibility |
|-----------|----------------|
| Demand Engine | Evaluate thermal demand |
| Source Engine | Select heating source |
| Protection Engine | Evaluate timing constraints |
| State Machine | Store logical thermostat state |

The Thermostat Controller coordinates these components but never duplicates their responsibilities.

---

# 6. Error Handling

If any engine raises an exception:

- terminate the current evaluation cycle;
- do not modify the State Machine;
- do not request any device action.

Error reporting outside the Thermostat Controller is the responsibility of the Home Assistant integration.

---

# 7. Source of Truth

This document defines the complete execution workflow of the Thermostat Controller.

The implementation shall strictly follow this workflow.

State transitions are defined exclusively in:

specs/11_controller_transition_table.md

Protection evaluation is defined exclusively in:

specs/12_controller_protection_workflow.md