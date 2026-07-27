# Smart Thermostat

## Device Action Generation

Version: 1.0

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

# 4. Outputs

The output is an ordered immutable collection of Requested Device Actions.

The collection may be empty.

An empty collection indicates that no physical device changes are required.

---

# 5. Boiler Actions

When the active heating source is the Boiler, the Thermostat Controller SHALL generate Boiler Requested Device Actions.

Possible actions include:

- Turn Boiler On;
- Turn Boiler Off.

No Climate Device actions shall be generated for heating while the Boiler is the active heating source.

---

# 6. Climate Device Actions

When the active device is a Climate Device, the Thermostat Controller SHALL generate Climate Requested Device Actions.

Possible actions include:

- Turn Climate On;
- Turn Climate Off;
- Set HVAC Mode;
- Set Target Temperature.

The requested target temperature SHALL be determined according to the Climate Control Table.

---

# 7. Cooling

Cooling always uses the configured Climate Device.

The Thermostat Controller SHALL generate the Requested Device Actions required for cooling.

The requested target temperature SHALL be determined according to the Climate Control Table.

---

# 8. Ordering

Requested Device Actions SHALL be generated in the order required for safe execution.

For a Climate Device the required order is:

1. Turn Climate On
2. Set HVAC Mode
3. Set Target Temperature

When turning a Climate Device off, only the required Turn Climate Off action shall be generated.

---

# 9. Idempotency

Requested Device Actions describe the desired physical state.

They do not imply that a Home Assistant service call will necessarily occur.

Device Controllers may suppress redundant service calls when the physical device already satisfies the requested state.

---

# 10. Completeness

The Requested Device Actions produced by the Thermostat Controller SHALL completely describe the desired physical state of every controlled device.

The Climate Entity shall not derive additional actions.

The Device Controllers shall not invent additional actions.

---

# 11. Source of Truth

This document defines how Requested Device Actions are generated.

Every implementation shall strictly follow this specification.