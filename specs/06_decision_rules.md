# Smart Thermostat

## Decision Rules

Version: 2.1

Status: Frozen

---

# 1. Purpose

This document defines the decision rules used by the Smart Thermostat.

Every decision is delegated to a specialized engine.

No component shall make decisions outside its responsibility.

---

# 2. Demand Evaluation

The Thermostat Controller requests the current thermal demand from the Demand Engine.

The Demand Engine receives the following inputs:

- current room temperature;
- heating target temperature;
- cooling target temperature;
- thermostat hysteresis;
- current thermostat state.

The current thermostat state is provided by the State Machine and is used exclusively to determine whether the thermostat is already heating or cooling, allowing the Demand Engine to correctly apply directional hysteresis.

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

# 3. Heating Source Selection

If the Demand Engine returns **HEATING**, the Thermostat Controller requests the heating source from the Source Engine.

The Source Engine compares:

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

# 4. Cooling Source

If the Demand Engine returns **COOLING**, the cooling source is always the configured air conditioner.

No source selection is required.

---

# 5. Protection Validation

Before applying any state transition or source change, the Thermostat Controller requests authorization from the Protection Engine.

The Protection Engine evaluates:

- shutdown delay;
- source change delay;
- minimum device runtime;
- minimum source runtime.

The Protection Engine returns exactly one result:

- ALLOWED
- DENIED

The Protection Engine never changes the requested action.

It only authorizes or rejects it.

---

# 6. State Machine

The State Machine stores only the logical operating state of the thermostat.

The Thermostat Controller is responsible for requesting state transitions.

The Demand Engine may read the current state in order to correctly apply thermostat hysteresis.

The Demand Engine shall never modify the State Machine.

The State Machine never stores:

- heating source;
- cooling source;
- photovoltaic surplus;
- timers;
- controller decisions.

---

# 7. Device Commands

Once all decisions have been completed:

1. The Demand Engine evaluates the thermal demand.
2. If heating is required, the Source Engine selects the heating source.
3. The Protection Engine validates the requested transition.
4. The State Machine updates the logical operating state.
5. The Thermostat Controller dispatches commands to the appropriate Device Controller.

---

# 8. Design Principles

Every engine answers exactly one question.

| Engine | Responsibility |
|--------|----------------|
| Demand Engine | Is there a thermal demand? |
| Source Engine | Which heating source should be used? |
| Protection Engine | Is the requested transition allowed? |
| State Machine | What is the current logical operating state? |
| Thermostat Controller | Orchestrate all components. |

The Demand Engine is the only component responsible for evaluating thermostat hysteresis.

The State Machine is the only component responsible for storing the logical operating state.

No component shall duplicate another component's responsibility.

---

# 9. Source of Truth

This document defines the official decision model of the Smart Thermostat.

Every implementation shall strictly follow these rules.