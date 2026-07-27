# Smart Thermostat

## Functional Specification

Version: 1.0

Status: Frozen

---

# 1. Purpose

This document defines the functional behaviour of the Smart Thermostat.

It specifies how the thermostat shall behave from the user's perspective.

Implementation details are intentionally excluded from this document.

---

# 2. Functional Overview

The Smart Thermostat is a virtual thermostat implemented as a standard Home Assistant Climate Entity.

The thermostat continuously evaluates the indoor temperature and automatically decides whether heating, cooling or no action is required.

When heating is required, the thermostat automatically selects the most appropriate heating source according to the configured energy strategy.

When cooling is required, the thermostat controls the configured cooling device.

The user interacts only with the Climate Entity.

The user never directly controls the internal decision process.

---

# 3. Climate Entity

The integration shall expose exactly one Climate Entity.

The entity shall behave as a native Home Assistant thermostat.

No custom frontend components shall be required.

---

# 4. HVAC Modes

The thermostat shall support only the following HVAC modes:

- Off
- Heat/Cool

No additional HVAC modes shall be implemented.

---

## Off

When the HVAC mode is Off:

- all controlled devices shall be turned off;
- no heating request shall be generated;
- no cooling request shall be generated.

---

## Heat/Cool

When the HVAC mode is Heat/Cool:

- the thermostat shall continuously evaluate the indoor temperature;
- the thermostat shall determine whether heating is required;
- the thermostat shall determine whether cooling is required;
- the thermostat shall remain idle when no action is required.

The thermostat shall automatically select the appropriate operating mode.

The user shall never manually choose between heating and cooling.

---

# 5. Target Temperatures

The thermostat shall expose two independent target temperatures.

Heating Target

Cooling Target

Both values shall be configurable through the standard Home Assistant Climate interface.

The thermostat shall internally use the appropriate target according to the current thermal demand.

---

# 6. Presets

The thermostat shall support the following presets:

- Away
- Home
- Night

The preset shall only represent the current operating context.

The integration shall never automatically change the preset.

Preset changes are managed externally by Home Assistant.

---

# 7. Input Entities

The thermostat shall receive the following entities as configuration parameters.

Heating Source 1

Primary heating device.

Typically a boiler.

Heating Source 2

Secondary heating device.

Typically an air conditioner operating in heating mode.

Cooling Source

Air conditioner operating in cooling mode.

Indoor Temperature Sensor

Temperature used by the thermostat.

Humidity Sensor

Humidity displayed by the Climate Entity.

Instantaneous Energy Surplus

Current photovoltaic surplus available.

Minimum Energy Surplus

Minimum surplus required to prefer the air conditioner over the boiler.

The integration assumes that every configured entity already provides the correct value.

The integration shall never perform calculations such as averages, filtering or sensor selection.

---

# 8. Thermal Demand

The thermostat shall continuously evaluate the indoor temperature.

The thermostat shall determine one of the following operating conditions:

- Heating Required
- Cooling Required
- No Thermal Demand

Only one thermal demand may exist at any given time.

Heating and cooling requests shall never coexist.

---

# 9. Heating Behaviour

When heating is required, the thermostat shall automatically select one heating source.

The selection shall be completely automatic.

The user shall not manually select the heating source.

Only one heating source may operate at any given time.

---

# 10. Cooling Behaviour

When cooling is required, the thermostat shall control the configured cooling device.

Only one cooling device may operate at any given time.

---

# 11. Heating Source Selection

The thermostat shall evaluate the available photovoltaic surplus.

If the available surplus satisfies the configured energy policy, the thermostat shall use the air conditioner for heating.

Otherwise, the thermostat shall use the boiler.

The selection process shall be completely automatic.

The thermostat shall protect physical devices from unnecessary source changes.

---

# 12. Device Protection

The thermostat shall minimize unnecessary switching of physical devices.

The thermostat shall include protection mechanisms for:

- compressors;
- boilers;
- source switching.

Protection mechanisms shall always have priority over fast reactions to temporary operating conditions.

---

# 13. Temperature Regulation

The thermostat shall regulate room temperature using the configured indoor temperature sensor.

The thermostat shall never rely on the internal temperature sensors of the air conditioner for thermal regulation.

The thermostat shall compensate for inaccuracies of the HVAC internal sensors.

---

# 14. Humidity

The humidity sensor is provided for information only.

Humidity shall be displayed by the Climate Entity.

Humidity shall not influence heating or cooling decisions.

---

# 15. HVAC Action

The thermostat shall expose the standard Home Assistant HVAC Action.

Possible values include:

- Off
- Idle
- Heating
- Cooling

The HVAC Action shall always represent the current operating state of the thermostat.

---

# 16. User Experience

From the user's perspective, the thermostat behaves as a standard Home Assistant thermostat.

The user shall only interact with:

- HVAC mode
- Heating target
- Cooling target
- Preset

All remaining decisions shall be performed automatically by the integration.

---

# 17. Functional Boundaries

The thermostat is responsible for:

- determining thermal demand;
- selecting the heating source;
- controlling the selected device;
- exposing a Climate Entity.

The thermostat is not responsible for:

- photovoltaic calculations;
- temperature averaging;
- sensor selection;
- presence detection;
- scheduling;
- automatic preset selection;
- home energy management.

These responsibilities remain external to the integration.

---

# 18. References

The implementation details described by this specification are defined in the following documents:

- 03_architecture.md
- 04_state_machine.md
- 05_control_algorithm.md
- 06_configuration.md
- 07_entities.md

This document defines only the functional behaviour of the thermostat.