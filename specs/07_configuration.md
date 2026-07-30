# Smart Thermostat

## Configuration

Version: 3.0

Status: Frozen

---

# 1. Purpose

This document defines every configurable parameter of the Smart Thermostat.

Configuration parameters customize the behaviour of the thermostat without modifying the control algorithm.

Only parameters defined in this document may be configured by the user.

---

# 2. Configuration Principles

Configuration shall only include installation-specific or user-specific parameters.

The following shall never be configurable:

- Software architecture
- State Machine
- Control Algorithm
- Decision Rules
- Protection Logic
- Control Curve structure

The thermostat behaviour shall remain identical regardless of configuration.

Only operating parameters may change.

---

# 3. General Configuration

## Name

Type

String

Description

Display name of the Climate Entity.

---

## Indoor Temperature Sensor

Type

Entity

Domain

sensor

Unit

°C

Description

Temperature used by the thermostat.

The integration assumes the configured sensor already provides the correct room temperature.

Temperature averaging, sensor selection and sensor filtering are outside the scope of this integration.

---

## Indoor Humidity Sensor

Type

Entity

Domain

sensor

Unit

%

Description

Humidity displayed by the Climate Entity.

Humidity is not used by the control algorithm.

---

# 4. Device Configuration

## Heating Source 1

Type

Entity

Domain

switch

Description

Primary heating source.

Heating Source 1 is intended to control a boiler through a dry contact.

The integration controls the entity exclusively through standard switch operations.

Support for boiler entities exposed as Climate devices is outside the scope of Version 1.

---

## Heating Source 2

Type

Entity

Domain

climate

Description

Secondary heating source.

Typically an air conditioner operating in heating mode.

The thermostat controls the HVAC operating mode and target temperature.

---

## Cooling Source

Type

Entity

Domain

climate

Description

Cooling source.

Typically the same physical air conditioner configured as Heating Source 2.

The thermostat controls the HVAC operating mode and target temperature.

---

# 5. Energy Configuration

## Instantaneous Energy Surplus

Type

Entity

Domain

sensor

Unit

W

Description

Current photovoltaic surplus available.

Positive values indicate available surplus.

The integration assumes that the configured sensor already provides the desired surplus calculation.

---

## Minimum Energy Surplus

Type

Entity

Domain

number

Unit

W

Description

Minimum photovoltaic surplus required to prefer the air conditioner over the boiler.

This value may be modified by the user at any time.

---

# 6. Thermostat Configuration

## Thermostat Tolerance

Type

Number

Unit

°C

Default

0.3°C

Description

Thermostat hysteresis.

The hysteresis is evaluated by the Demand Engine together with the current logical thermostat state provided by the State Machine.

The hysteresis is applied only when starting a new heating or cooling request.

Once a request is active, it continues until the corresponding target temperature is reached.

Heating Request starts when:

```
Current Temperature ≤ Heating Target − Tolerance
```

Heating Request ends when:

```
Current Temperature ≥ Heating Target
```

Cooling Request starts when:

```
Current Temperature ≥ Cooling Target + Tolerance
```

Cooling Request ends when:

```
Current Temperature ≤ Cooling Target
```

This behaviour implements directional hysteresis and prevents unnecessary heating and cooling cycles while maintaining the desired target temperature.

---

# 7. Protection Configuration

## Shutdown Delay

Type

Duration

Description

Time the currently operating device remains active after thermal demand disappears.

This delay applies only while the Climate Device is the active heating or cooling
solution (Heating via the Climate Device, or Cooling). It never applies while the
Boiler is the active heating solution - the Boiler stops immediately once thermal
demand disappears, subject only to Minimum Runtime.

Purpose

Prevent unnecessary compressor cycling. Radiator-based Boiler heating already has
significant thermal inertia; keeping it running after demand has ended would only
inject additional heat and cause unnecessary overshoot.

---

## Source Change Delay

Type

Duration

Description

Minimum time the desired heating source must remain different from the current heating source before a source transition is allowed.

Purpose

Ignore temporary photovoltaic fluctuations.

---

## Minimum Runtime

Type

Duration

Description

Minimum amount of time the currently active heating or cooling solution (Boiler or
Climate Device) must remain active before it can be stopped or replaced by a
different heating source.

Purpose

Protect compressors and boilers from excessive switching.

---

# 8. Internal Calibration Parameters

The following parameters are internal software calibration parameters.

They are intentionally not configurable.

---

## Heating Control Curve

Defines the mapping between:

- Temperature Error
- HVAC Target Temperature

Only the calibration values may evolve between software versions.

The evaluation algorithm is fixed.

---

## Cooling Control Curve

Defines the mapping between:

- Temperature Error
- HVAC Target Temperature

Only the calibration values may evolve between software versions.

The evaluation algorithm is fixed.

---

# 9. Default Calibration Values

The numerical values of the Heating Control Curve and Cooling Control Curve are intentionally excluded from this document.

The calibration values belong to the software implementation.

Future software versions may refine these values without modifying the documented algorithms.

---

# 10. Configuration Validation

The integration shall validate every configuration parameter before becoming operational.

Validation shall include:

- entity existence;
- correct entity domain;
- supported unit of measurement;
- parameter consistency.

Invalid configurations shall prevent the integration from starting.

---

# 11. Source of Truth

This document defines every configurable parameter supported by the Smart Thermostat.

Any parameter not documented here shall be considered part of the internal implementation.

Any new configurable parameter requires an explicit update of this document.