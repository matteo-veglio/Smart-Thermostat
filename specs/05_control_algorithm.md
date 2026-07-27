# Smart Thermostat

## Control Algorithm

Version: 2.0

Status: Frozen

---

# 1. Purpose

This document defines the thermal demand evaluation algorithm used by the Smart Thermostat.

The algorithm is implemented exclusively by the Demand Engine.

The Demand Engine evaluates only whether heating, cooling or no thermal demand currently exists.

It never selects the heating source.

It never evaluates protection logic.

---

# 2. Inputs

The Demand Engine receives the following inputs:

| Input | Description |
|--------|-------------|
| Current Room Temperature | Current measured room temperature. |
| Heating Target Temperature | User heating setpoint. |
| Cooling Target Temperature | User cooling setpoint. |
| Thermostat Hysteresis | Configured thermostat hysteresis. |
| Current Thermostat State | Current logical state provided by the State Machine. |

The Current Thermostat State is read-only.

The Demand Engine shall never modify the State Machine.

---

# 3. Outputs

The Demand Engine returns exactly one value:

- NO_DEMAND
- HEATING
- COOLING

No other outputs are allowed.

---

# 4. Heating Algorithm

The algorithm behaves differently depending on the current thermostat state.

## Heating Start

If the current thermostat state is NOT `HEATING`:

Heating demand begins when:

```
Current Temperature ≤ Heating Target − Hysteresis
```

## Heating Stop

If the current thermostat state is `HEATING`:

Heating demand ends when:

```
Current Temperature ≥ Heating Target
```

Otherwise, the engine continues requesting HEATING.

---

# 5. Cooling Algorithm

The algorithm behaves differently depending on the current thermostat state.

## Cooling Start

If the current thermostat state is NOT `COOLING`:

Cooling demand begins when:

```
Current Temperature ≥ Cooling Target + Hysteresis
```

## Cooling Stop

If the current thermostat state is `COOLING`:

Cooling demand ends when:

```
Current Temperature ≤ Cooling Target
```

Otherwise, the engine continues requesting COOLING.

---

# 6. Idle Condition

If neither the heating nor cooling conditions are satisfied, the engine returns:

```
NO_DEMAND
```

---

# 7. Responsibilities

The Demand Engine SHALL:

- evaluate thermal demand;
- apply thermostat hysteresis;
- use the current thermostat state only to determine the correct hysteresis threshold;
- return exactly one demand.

The Demand Engine SHALL NOT:

- modify the State Machine;
- select heating sources;
- evaluate photovoltaic surplus;
- execute timers;
- execute protection logic;
- communicate with Home Assistant.

---

# 8. Source of Truth

This document is the only definition of the Smart Thermostat demand evaluation algorithm.

Every implementation shall strictly follow this specification.