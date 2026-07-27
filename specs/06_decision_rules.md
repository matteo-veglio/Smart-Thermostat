# Smart Thermostat

## Decision Rules

Version: 1.0

Status: Frozen

---

# 1. Purpose

This document defines every decision rule used by the Smart Thermostat.

Decision rules determine **when** an action is allowed.

The control algorithm defines **how** the thermostat operates.

The decision rules define **whether** an operation may be executed.

---

# 2. General Principles

Every decision made by the thermostat shall follow documented rules.

Decision rules shall always produce deterministic results.

The same inputs and the same internal state shall always produce the same decision.

Decision rules shall never directly control physical devices.

Their only purpose is to authorize or deny operations.

---

# 3. Thermal Demand Decision

The thermostat shall evaluate the indoor temperature using the configured target temperatures and thermostat tolerance.

The possible outcomes are:

- Heating Required
- Cooling Required
- No Thermal Demand

Only one outcome may exist during a control cycle.

Heating and cooling shall never be requested simultaneously.

The detailed thermal demand calculation is defined by the thermostat tolerance configuration.

---

# 4. Heating Source Decision

When heating is required, the thermostat shall determine which heating source should be used.

Possible heating sources are:

- Boiler
- Air Conditioner

The decision shall consider:

- instantaneous energy surplus;
- minimum energy surplus;
- current operating state;
- protection rules.

Only one heating source may be active.

---

# 5. Heating Source Change Decision

A heating source change shall only be allowed when all required conditions are satisfied.

The thermostat shall never continuously alternate between heating sources due to temporary operating conditions.

Source switching shall be protected by dedicated protection rules.

The detailed protection parameters are defined in the configuration document.

---

# 6. Cooling Decision

Cooling shall always use the configured air conditioner.

No alternative cooling sources are supported.

---

# 7. Control Curve Decision

The Climate Controller shall determine the HVAC target temperature using a Control Curve.

The Control Curve shall consist of ordered intervals.

Each interval shall contain:

- Minimum Temperature Error
- HVAC Target Temperature

The algorithm shall evaluate the intervals from top to bottom.

The first matching interval shall always be selected.

The resulting HVAC target temperature shall be used for the current control cycle.

---

# 8. Heating Control Curve

Heating regulation shall use a dedicated Heating Control Curve.

The Heating Control Curve shall satisfy the following rules.

- The intervals shall be ordered by decreasing temperature error.
- Each interval shall be evaluated independently.
- Only one interval may be selected.
- HVAC target temperatures shall increase monotonically as the temperature error increases.

The numerical values of the curve are calibration parameters.

The evaluation method is part of the algorithm and shall never change.

---

# 9. Cooling Control Curve

Cooling regulation shall use a dedicated Cooling Control Curve.

The Cooling Control Curve shall satisfy the following rules.

- The intervals shall be ordered by decreasing temperature error.
- Each interval shall be evaluated independently.
- Only one interval may be selected.
- HVAC target temperatures shall decrease monotonically as the temperature error increases.

The numerical values of the curve are calibration parameters.

The evaluation method is part of the algorithm and shall never change.

---

# 10. Command Update Decision

The thermostat shall compare the requested operating values with the current device state.

Commands shall only be generated when an operating value changes.

Repeated identical commands are forbidden.

---

# 11. Shutdown Decision

The thermostat shall never immediately stop an operating device when thermal demand ends.

The shutdown decision shall always be delayed.

During the delay period:

- thermal demand shall continue to be evaluated;
- the shutdown may be cancelled if thermal demand returns.

Only after the complete delay expires may the operating device be turned off.

---

# 12. Minimum Runtime Decision

Every controlled device shall remain active for a configurable minimum runtime.

The thermostat shall never stop a device before the minimum runtime expires.

Emergency shutdown conditions are outside the scope of this document.

---

# 13. Minimum Source Runtime Decision

After selecting a heating source, the thermostat shall maintain the selected source for a configurable minimum duration.

Temporary fluctuations of photovoltaic surplus shall not immediately trigger a source change.

The objective is to minimize unnecessary boiler and compressor cycling.

---

# 14. Protection Priority

Protection rules always have higher priority than operating requests.

Whenever a protection rule conflicts with a normal operating request, the protection rule shall prevail.

---

# 15. Calibration Principles

The following elements are considered calibration parameters:

- Heating Control Curve values;
- Cooling Control Curve values;
- Thermostat tolerance;
- Shutdown delay;
- Minimum runtime;
- Minimum source runtime;
- Minimum energy surplus.

Calibration parameters may change without modifying the decision rules.

---

# 16. Source of Truth

This document defines every decision rule used by the Smart Thermostat.

The implementation shall never introduce undocumented decision logic.

Any modification of the decision process requires an explicit update of this document.