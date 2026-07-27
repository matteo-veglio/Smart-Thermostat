# Smart Thermostat

## Control Algorithm

Version: 1.0

Status: Frozen

---

# 1. Purpose

This document defines the complete control algorithm of the Smart Thermostat.

The algorithm specifies how the thermostat processes its inputs, determines the required operating strategy and generates commands for the controlled devices.

The algorithm is deterministic.

Given the same inputs and the same internal state, it shall always produce the same output.

---

# 2. Control Cycle

The thermostat operates using a periodic control cycle.

Each execution of the control cycle is completely independent.

Every control cycle shall execute the following phases in the specified order.

1. Read Inputs

2. Evaluate Thermal Demand

3. Evaluate State Machine

4. Select Operating Strategy

5. Select Heating Source

6. Apply Protection Rules

7. Generate Device Commands

8. Update Climate Entity

The execution order shall never change.

---

# 3. Read Inputs

The thermostat shall read every configured entity.

The control algorithm shall never use cached entity values.

Every control cycle shall use the latest available Home Assistant state.

The following values shall be acquired:

- Indoor temperature
- Indoor humidity
- HVAC mode
- Preset
- Heating target temperature
- Cooling target temperature
- Instantaneous energy surplus
- Minimum energy surplus
- Current device states

---

# 4. Evaluate Thermal Demand

The thermostat shall determine whether thermal demand exists.

Possible outcomes are:

- Heating Required
- Cooling Required
- No Demand

The thermal demand calculation is independent from every physical device.

The thermal demand calculation shall not consider:

- boiler state
- air conditioner state
- photovoltaic surplus
- protection timers

---

# 5. Evaluate State Machine

The thermostat shall evaluate the current operating state.

The current state determines which transitions are allowed.

The algorithm shall never bypass the State Machine.

State transitions are defined in:

04_state_machine.md

---

# 6. Select Operating Strategy

The thermostat shall determine the required operating strategy.

Possible strategies are:

- Idle
- Heating
- Cooling

Only one operating strategy may exist during a control cycle.

---

# 7. Select Heating Source

Heating source selection is executed only when the operating strategy is Heating.

The algorithm shall evaluate the configured energy policy.

Possible heating sources are:

- Boiler
- Air Conditioner

Only one heating source may be selected.

The selected heating source shall remain active until a valid source transition is permitted.

---

# 8. Apply Protection Rules

Before generating any command, the thermostat shall evaluate every protection rule.

Protection rules may temporarily prevent state transitions or device commands.

Protection rules include:

- minimum device runtime;
- minimum source runtime;
- shutdown delay;
- source switching protection.

Protection rules always have priority over operating requests.

---

# 9. Generate Device Commands

The thermostat shall generate commands according to the selected operating strategy.

Possible commands include:

- Boiler ON
- Boiler OFF
- HVAC Mode
- HVAC Target Temperature
- HVAC OFF

The generated commands depend on the active operating state.

---

# 10. Climate Regulation

The air conditioner shall never regulate room temperature using its internal temperature sensor.

Room temperature regulation is performed exclusively by the Smart Thermostat.

The thermostat controls the air conditioner by adjusting its target temperature.

---

# 11. Heating Control Curve

Heating regulation shall use a discrete control curve.

Input:

Temperature Error

Output:

HVAC Target Temperature

The algorithm shall evaluate the configured Heating Control Curve.

The first matching interval shall be selected.

The corresponding HVAC target temperature shall be applied.

The control curve definition is part of the system configuration.

The numerical values of the control curve are calibration parameters.

---

# 12. Cooling Control Curve

Cooling regulation shall use a discrete control curve.

Input:

Temperature Error

Output:

HVAC Target Temperature

The algorithm shall evaluate the configured Cooling Control Curve.

The first matching interval shall be selected.

The corresponding HVAC target temperature shall be applied.

The control curve definition is part of the system configuration.

The numerical values of the control curve are calibration parameters.

---

# 13. Command Optimization

The thermostat shall never send unnecessary commands.

A command shall only be generated when the requested operating value differs from the current operating value.

Repeated identical commands are forbidden.

---

# 14. Climate Entity Update

At the end of every control cycle the Climate Entity shall be updated.

The entity shall always represent the current operating state of the thermostat.

---

# 15. Algorithm Principles

The control algorithm shall satisfy the following principles.

Deterministic

The same inputs always generate the same outputs.

Predictable

Every decision follows documented rules.

Stateless Decisions

Every decision depends only on:

- current inputs;
- current configuration;
- current State Machine state.

Calibrated Behaviour

Algorithm behaviour shall remain unchanged when calibration values are modified.

Calibration parameters shall never change the structure of the algorithm.

---

# 16. Source of Truth

This document defines the complete operating algorithm of the Smart Thermostat.

Any modification of the algorithm requires an explicit update of this document.