# Smart Thermostat

## Requested Device Actions

Version: 1.3

Status: Frozen

---

# 1. Purpose

This document defines the Requested Device Actions produced by the Thermostat Controller.

Requested Device Actions represent the physical modifications required to transform the current physical device state into the physical device state determined by the Thermostat Controller during the current evaluation cycle.

They are consumed by the Home Assistant integration layer.

They are the only mechanism through which the domain requests changes to physical devices.

Requested Device Actions represent only the physical modifications that are required.

---

# 2. Responsibilities

The Thermostat Controller SHALL:

- determine the requested thermostat state;
- determine the requested operation;
- determine the requested climate device target temperature when required;
- compare the current physical device state with the physical device state implied by those decisions;
- generate only the Requested Device Actions required to reach that physical device state;
- return the complete list of Requested Device Actions as part of the ThermostatControllerResult.

The Climate Entity SHALL:

- receive the Requested Device Actions;
- execute them in the order received.

The Device Controllers SHALL:

- translate Requested Device Actions into Home Assistant service calls.

No other component shall create, modify or execute Requested Device Actions.

---

# 3. Design Principles

Requested Device Actions are immutable.

They are domain objects.

They contain no Home Assistant specific information.

They represent only the physical modifications required to apply the Thermostat Controller decision.

They never describe the complete physical device configuration.

They never describe how Home Assistant shall execute the operation.

---

# 4. Thermostat Controller Result

The ThermostatControllerResult SHALL contain:

- Current Thermostat State;
- Current Operation;
- Current Heating Source;
- Requested Device Actions.

Requested Device Actions SHALL be represented as an ordered immutable collection.

The order SHALL be preserved during execution.

The collection MAY be empty.

An empty collection explicitly means that the current physical device state already matches the physical device state determined by the Thermostat Controller.

---

# 5. Device Action

A Device Action represents exactly one required physical modification.

Every Device Action SHALL:

- target exactly one logical device;
- represent exactly one required operation;
- contain only the parameters required by that operation.

Device Actions shall never contain optional unused parameters.

---

# 6. Logical Devices

Requested Device Actions target logical devices.

Initially the following logical devices exist:

- Boiler
- Climate Device

Logical devices are independent from Home Assistant entities.

---

# 7. Supported Operations

Initially the Smart Thermostat supports the following operations.

## Boiler

- Turn On
- Turn Off

## Climate Device

- Turn On
- Turn Off
- Set HVAC Mode
- Set Target Temperature

Future operations shall be introduced by extending the model.

Existing operations shall never change semantics.

---

# 8. Execution Order

Requested Device Actions SHALL be executed exactly in the order produced by the Thermostat Controller.

The Climate Entity SHALL NOT:

- reorder actions;
- merge actions;
- discard actions;
- generate additional actions.

---

# 9. Idempotency

The Thermostat Controller SHALL NOT generate Requested Device Actions that do not represent a required physical modification.

Device Controllers may still suppress redundant Home Assistant service calls caused by external device state changes or communication races.

This optimization shall never modify the Requested Device Actions produced by the Thermostat Controller.

---

# 10. Independence

Requested Device Actions are completely independent from:

- Home Assistant;
- device integrations;
- manufacturers;
- communication protocols.

They belong exclusively to the Smart Thermostat domain.

---

# 11. Source of Truth

This document defines the Requested Device Action contract exchanged between the Smart Thermostat domain and the Home Assistant integration.

Every implementation shall strictly follow this specification.