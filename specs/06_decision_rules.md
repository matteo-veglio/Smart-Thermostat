# Smart Thermostat

## Decision Rules

Version: 2.0

Status: Frozen

---

# 1. Purpose

This document defines the decision rules used by the Smart Thermostat.

Every decision is delegated to a specialized engine.

No component shall make decisions outside its responsibility.

---

# 2. Demand Evaluation

The Demand Engine evaluates the thermal demand.

Possible outputs are:

- NO_DEMAND
- HEATING
- COOLING

The Demand Engine evaluates only:

- current room temperature;
- heating target temperature;
- cooling target temperature;
- thermostat hysteresis.

The Demand Engine never evaluates:

- photovoltaic surplus;
- heating source;
- protection timers.

---

# 3. Heating Source Selection

If the Demand Engine requests HEATING, the Thermostat Controller requests the heating source from the Source Engine.

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

---

# 4. Cooling Source

Cooling always uses the configured air conditioner.

No source selection is required.

---

# 5. Protection Validation

Before applying any state or source change, the Thermostat Controller asks the Protection Engine whether the transition is allowed.

The Protection Engine evaluates:

- shutdown delay;
- source change delay;
- minimum device runtime;
- minimum source runtime.

The Protection Engine returns either:

- ALLOWED
- DENIED

It never changes the decision itself.

---

# 6. State Machine

The Thermostat Controller updates the State Machine only after the Protection Engine has approved the transition.

The State Machine stores only the logical operating state.

It never stores:

- heating source;
- cooling source;
- photovoltaic surplus;
- timers.

---

# 7. Device Commands

After all decisions have been completed:

1. Demand Engine determines the thermal demand.
2. Source Engine selects the heating source (heating only).
3. Protection Engine validates the transition.
4. State Machine updates the logical operating state.
5. Thermostat Controller dispatches commands to the appropriate Device Controller.

---

# 8. Design Principles

Every engine answers exactly one question.

| Engine | Question |
|--------|----------|
| Demand Engine | Is heating or cooling required? |
| Source Engine | Which heating source shall be used? |
| Protection Engine | Is the requested transition currently allowed? |
| State Machine | What is the current logical operating state? |
| Thermostat Controller | How are all engines orchestrated? |

No engine shall duplicate another engine's responsibility.

---

# 9. Source of Truth

This document defines the official decision model of the Smart Thermostat.

Every implementation shall strictly follow these rules.