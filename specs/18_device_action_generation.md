# Smart Thermostat

## Device Action Generation

Version: 1.1

Status: Frozen

---

# 1. Purpose

This document defines how the Thermostat Controller generates Requested Device Actions.

Requested Device Actions represent the desired physical state of every controlled device after a thermostat evaluation.

The Thermostat Controller is the only component responsible for generating them.

---

# 2. Responsibilities

The Thermostat Controller SHALL:

- compare the desired system state with the current system state;
- determine which physical changes are required;
- determine the requested Climate Device target temperature when required;
- generate the corresponding Requested Device Actions.

The Thermostat Controller SHALL NOT:

- communicate with Home Assistant;
- invoke Device Controllers;
- execute Home Assistant services.

---

# 3. Inputs

The Device Action generation process receives:

- Current Thermostat State;
- Current Operation;
- Current Heating Source;
- Requested Thermostat State;
- Runtime Context.

No additional inputs shall be required.

---

# 4. Climate Control Table

The Climate Control Table is part of the Thermostat Controller domain logic.

Whenever a Climate Device target temperature is required, the Thermostat Controller SHALL evaluate the Climate Control Table before generating the Requested Device Actions.

The Device Action generation process receives the resulting target temperature.

The Device Action generation process SHALL NOT evaluate the Climate Control Table.

---

# 5. Outputs

The output is an ordered immutable collection of Requested Device Actions.

The collection MAY be empty.

An empty collection explicitly means that no physical device changes are required.

---

# 6. Boiler Actions

When the active heating source is the Boiler, the Thermostat Controller SHALL generate Boiler Requested Device Actions.

Possible actions include:

- Turn Boiler On;
- Turn Boiler Off.

No Climate Device actions shall be generated for heating while the Boiler is the active heating source.

---

# 7. Climate Device Actions

When the active device is a Climate Device, the Thermostat Controller SHALL generate Climate Requested Device Actions.

Possible actions include:

- Turn Climate On;
- Turn Climate Off;
- Set HVAC Mode;
- Set Target Temperature.

The requested target temperature SHALL be the value previously determined by the Thermostat Controller through the Climate Control Table.

The Device Action generation process SHALL never calculate or modify the requested target temperature.

---

# 8. Cooling

Cooling always uses the configured Climate Device.

The Thermostat Controller SHALL generate the Requested Device Actions required for cooling.

The requested target temperature SHALL be the value previously determined through the Climate Control Table.

---

# 9. Ordering

Requested Device Actions SHALL be generated in the order required for safe execution.

For a Climate Device the required order is:

1. Turn Climate On
2. Set HVAC Mode
3. Set Target Temperature

When turning a Climate Device off, only the required Turn Climate Off action shall be generated.

---

# 10. Idempotency

Requested Device Actions represent the desired physical state.

They do not imply that a Home Assistant service call will necessarily occur.

Device Controllers may suppress redundant Home Assistant service calls when the physical device already satisfies the requested state.

This optimization shall never modify the Requested Device Actions.

---

# 11. Completeness

The Requested Device Actions produced by the Thermostat Controller SHALL completely describe the desired physical state of every controlled device.

The Climate Entity shall not derive additional actions.

The Device Controllers shall not invent additional actions.

---

# 12. Source of Truth

This document defines how Requested Device Actions are generated.

Every implementation shall strictly follow this specification.