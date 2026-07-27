# Smart Thermostat

## Control Algorithm

Version: 2.1

Status: Frozen

---

# 1. Purpose

This document defines the thermal demand evaluation algorithm used by the Smart Thermostat.

The algorithm is implemented exclusively by the Demand Engine.

The Demand Engine evaluates only whether heating, cooling or no thermal demand currently exists.

It never selects the heating source.

It never evaluates protection logic.

---

# 2. Runtime Context

The Demand Engine receives a Runtime Context.

The Runtime Context contains every runtime value required by the domain layer.

The Demand Engine reads only the information required for thermal demand evaluation.

The Runtime Context is immutable.

The Demand Engine never modifies it.

---

# 3. Inputs Used by the Demand Engine

From the Runtime Context, the Demand Engine reads:

| Runtime Context Field | Description |
|-----------------------|-------------|
| Current Room Temperature | Current measured room temperature. |
| Heating Target Temperature | User heating setpoint. |
| Cooling Target Temperature | User cooling setpoint. |
| Thermostat Hysteresis | Configured thermostat hysteresis. |
| Current Thermostat State | Current logical thermostat state. |

No other Runtime Context fields participate in the thermal demand calculation.

---

# 4. Outputs

The Demand Engine returns exactly one value:

- NO_DEMAND
- HEATING
- COOLING

No other outputs are allowed.

---

# 5. Heating Algorithm

The algorithm behaves differently depending on the current thermostat state.

## Heating Start

If the current thermostat state is NOT `HEATING`:

Heating demand begins when:

```
Current Temperature ≤ Heating Target − Hysteresis
```

## Heating Continue

If the current thermostat state is `HEATING`:

Heating demand continues while:

```
Current Temperature < Heating Target
```

Otherwise the Demand Engine returns:

```
NO_DEMAND
```

---

# 6. Cooling Algorithm

The algorithm behaves differently depending on the current thermostat state.

## Cooling Start

If the current thermostat state is NOT `COOLING`:

Cooling demand begins when:

```
Current Temperature ≥ Cooling Target + Hysteresis
```

## Cooling Continue

If the current thermostat state is `COOLING`:

Cooling demand continues while:

```
Current Temperature > Cooling Target
```

Otherwise the Demand Engine returns:

```
NO_DEMAND
```

---

# 7. Idle Condition

If neither heating nor cooling conditions are satisfied:

```
NO_DEMAND
```

is returned.

---

# 8. Responsibilities

The Demand Engine SHALL:

- evaluate thermal demand;
- apply thermostat hysteresis;
- read only the Runtime Context fields required for demand evaluation;
- return exactly one demand.

The Demand Engine SHALL NOT:

- modify the Runtime Context;
- modify the State Machine;
- select heating sources;
- evaluate photovoltaic surplus;
- execute timers;
- execute protection logic.

---

# 9. Source of Truth

This document defines the official demand evaluation algorithm of the Smart Thermostat.

Every implementation shall strictly follow this specification.