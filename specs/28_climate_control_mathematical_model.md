# Climate Control Mathematical Model

## 1. Purpose

This specification defines exclusively the mathematical model used to continuously regulate the Climate Device target temperature.

It is intentionally independent from the Smart Thermostat architecture.

This document defines:

- the mathematical control law;
- controller parameters;
- controller internal state;
- controller inputs;
- controller output.

This document does **not** define:

- thermostat behaviour;
- thermostat state transitions;
- heating or cooling demand evaluation;
- heating source selection;
- HVAC mode selection;
- protection rules;
- device actions;
- Smart Thermostat architecture.

Those responsibilities are defined by the Smart Thermostat architectural specifications.

The mathematical algorithm defined in this document shall remain independent from the component that executes it.

---

# 2. Control Objective

The objective of the controller is to continuously calculate the optimal Climate Device target temperature required to reach the desired room temperature.

The controller receives:

- the desired room temperature;
- the measured room temperature.

The controller produces:

- the Climate Device target temperature.

The controller shall be usable for both Heating and Cooling without changing the sign of the controller gains.

---

# 3. Controller Model

The controller is composed of three mathematical components:

- Proportional (P)
- Integral (I)
- Feedforward (FF)

The controller also implements:

- Anti-Windup using Back-Calculation.

---

# 4. Inputs

| Symbol | Type | Unit | Description |
|---------|------|------|-------------|
| `TRoom_Set` | float | °C | Desired room temperature |
| `TRoom` | float | °C | Measured room temperature |

---

# 5. Output

| Symbol | Type | Unit | Description |
|---------|------|------|-------------|
| `TAc_Set` | float | °C | Climate Device target temperature |

---

# 6. Configuration Parameters

| Symbol | Unit | Description |
|---------|------|-------------|
| `Kp` | - | Proportional gain |
| `Ti` | s | Integral time |
| `Tt` | s | Anti-Windup tracking time |
| `Ts` | s | Sampling period |
| `TAc_min` | °C | Minimum Climate Device temperature |
| `TAc_max` | °C | Maximum Climate Device temperature |

No mathematical constant shall be hardcoded inside the control algorithm.

Every parameter shall be configurable.

---

# 7. Persistent Controller State

The controller maintains the following internal state.

| Variable | Initial Value | Description |
|----------|---------------|-------------|
| `I_prev` | 0.0 | Previous integral state |
| `Desat_prev` | 0.0 | Previous anti-windup tracking state |

These values shall persist between consecutive controller evaluations.

---

# 8. Heating and Cooling Behaviour

The same mathematical equations shall be used for both Heating and Cooling.

No sign inversion of the controller gains shall be performed.

Heating example:

```
TRoom < TRoom_Set
↓

Err > 0
↓

TAc_Set > TRoom_Set
```

Cooling example:

```
TRoom > TRoom_Set
↓

Err < 0
↓

TAc_Set < TRoom_Set
```

---

# 9. Mathematical Algorithm

At every controller evaluation the following equations shall be executed **exactly in the order shown**.

## Step 1

Compute instantaneous error.

```
Err(k) = TRoom_Set(k) − TRoom(k)
```

---

## Step 2

Compute proportional term.

```
P(k) = Kp · Err(k)
```

---

## Step 3

Compute integral term using Anti-Windup Back-Calculation.

```
I(k) = I_prev
     + P(k) · Ts / Ti
     + Desat_prev · Ts / Tt
```

---

## Step 4

Compute PI output.

```
Y(k) = P(k) + I(k)
```

---

## Step 5

Apply Feedforward.

```
Ytot(k) = Y(k) + TRoom_Set(k)
```

The PI controller therefore computes only the corrective temperature offset.

---

## Step 6

Apply output saturation.

```
TAc_Set(k) =
max(
    TAc_min,
    min(
        TAc_max,
        Ytot(k)
    )
)
```

---

## Step 7

Compute Anti-Windup tracking error.

```
Desat(k) = TAc_Set(k) − Ytot(k)
```

---

## Step 8

Update controller state.

```
I_prev ← I(k)

Desat_prev ← Desat(k)
```

---

# 10. Controller Reset

Whenever the execution environment requests a controller reset, the internal state shall become:

```
I_prev = 0.0

Desat_prev = 0.0
```

This document intentionally does not define when a reset shall occur.

That decision belongs to the Smart Thermostat architecture.

---

# 11. Invalid Inputs

If one or more controller inputs are invalid:

- None
- NaN
- unavailable
- unknown

the controller evaluation shall be aborted.

The previous controller state shall remain unchanged.

The previous valid controller output shall remain available to the caller.

---

# 12. Mathematical Invariants

The following statements shall always remain true.

- The controller computes exactly one output.
- The controller is deterministic.
- The controller contains no thermostat logic.
- The controller contains no Home Assistant logic.
- The controller contains no scheduling logic.
- The controller contains no device selection logic.
- The controller contains no HVAC mode logic.
- The controller is reusable in any execution environment.

---

# 13. Compliance

Any implementation claiming compliance with this specification shall:

- execute the mathematical equations exactly as defined;
- preserve controller state between evaluations;
- implement Feedforward exactly as specified;
- implement Anti-Windup using Back-Calculation;
- preserve the equation execution order;
- produce identical numerical behaviour for identical inputs and parameters.