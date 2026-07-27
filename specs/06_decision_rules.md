# Smart Thermostat

## Decision Rules

Version: 2.2

Status: Frozen

---

# 1. Purpose

This document defines the decision rules used by the Smart Thermostat.

Every decision is delegated to a specialized component.

No component shall make decisions outside its responsibility.

---

# 2. Runtime Context

Every thermostat evaluation starts with a Runtime Context.

The Runtime Context contains every runtime value required by the domain layer.

The Runtime Context is created by the Runtime Context Factory.

The Runtime Context is immutable.

Every domain component reads only the information required for its own evaluation.

No domain component shall retrieve information directly from Home Assistant.

---

# 3. Demand Evaluation

The Thermostat Controller requests the current thermal demand from the Demand Engine.

The Demand Engine receives the Runtime Context.

It reads only:

- current room temperature;
- heating target temperature;
- cooling target temperature;
- thermostat hysteresis;
- current thermostat state.

The Demand Engine returns exactly one value:

- NO_DEMAND
- HEATING
- COOLING

The Demand Engine never:

- modifies the State Machine;
- selects the heating source;
- evaluates photovoltaic surplus;
- evaluates protection rules.

---

# 4. Heating Source Selection

If the Demand Engine returns **HEATING**, the Thermostat Controller requests the preferred heating source from the Source Engine.

The Source Engine receives the Runtime Context.

It reads only:

- instantaneous energy surplus;
- minimum energy surplus.

Decision:

If:

```
Instantaneous Surplus ≥ Minimum Surplus
```

Heating Source:

```
AIR_CONDITIONER
```

Otherwise:

```
BOILER
```

The Source Engine performs no other evaluations.

---

# 5. Cooling Source

If the Demand Engine returns **COOLING**, the cooling source is always the configured Cooling Source.

No source selection is required.

---

# 6. Requested State Selection

The Thermostat Controller requests the next logical thermostat state from the Transition Table.

The Transition Table receives:

- current thermostat state;
- current demand.

It returns:

- requested thermostat state.

The Thermostat Controller never derives transition rules.

---

# 7. Protection Validation

Whenever a state transition or heating source change is requested, the Thermostat Controller invokes the Protection Engine according to:

- specs/12_controller_protection_workflow.md

The Protection Engine receives the Runtime Context.

It reads only the timing values required for the requested protection check.

The Protection Engine returns exactly one value:

- ALLOWED
- DENIED

The Protection Engine never changes the requested action.

---

# 8. State Machine

If the Protection Engine authorizes the requested transition:

The Thermostat Controller requests the State Machine to update the logical thermostat state.

The State Machine stores only:

- OFF
- IDLE
- STARTING
- HEATING
- COOLING
- STOPPING

The State Machine never stores:

- heating source;
- cooling source;
- photovoltaic surplus;
- timers;
- controller decisions.

---

# 9. Device Commands

After all domain decisions have been completed:

The Thermostat Controller requests the appropriate Device Controller to execute the required action.

Device Controllers never make decisions.

They execute commands only.

---

# 10. Design Principles

Every component answers exactly one question.

| Component | Responsibility |
|----------|----------------|
| Runtime Context Factory | Collect runtime information |
| Runtime Context | Transport runtime information |
| Demand Engine | Is there thermal demand? |
| Transition Table | Which logical state is requested? |
| Source Engine | Which heating source should be used? |
| Protection Engine | Is the requested operation allowed? |
| State Machine | What is the current logical thermostat state? |
| Thermostat Controller | Orchestrate the domain components |
| Device Controllers | Execute device commands |

No component shall duplicate another component's responsibility.

---

# 11. Source of Truth

This document defines the official decision model of the Smart Thermostat.

Every implementation shall strictly follow these rules.