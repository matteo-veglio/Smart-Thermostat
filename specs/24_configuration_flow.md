# Configuration Flow

## 1. Purpose

The Configuration Flow defines how a Smart Thermostat instance is configured through the Home Assistant user interface.

Its only responsibility is collecting and validating user configuration.

It never implements thermostat behaviour.

---

## 2. Configuration Flow

The Configuration Flow shall be organized into the following steps:

1. General
2. Devices
3. Energy
4. Protection
5. Home Preset
6. Away Preset
7. Sleep Preset

Each step shall collect only the configuration belonging to that category.

---

## 3. General Step

The General step shall collect:

- Name

---

## 4. Devices Step

The Devices step shall collect:

### Climate Device

Climate entity controlled by the Smart Thermostat.

### Boiler

Switch entity controlling the boiler.

The Boiler is a fundamental part of the Smart Thermostat's hybrid heating source
selection and shall therefore always be explicitly configured.

The Boiler field shall behave exactly like the Climate Device field: a mandatory,
searchable Home Assistant Entity Selector, with no default value, no placeholder
option, and no representation for "no Boiler."

A configuration without a Boiler is invalid by definition. The Configuration Flow shall
not allow completion, and the Options Flow shall not allow saving, until a valid Boiler
switch entity has been selected. Validation shall reject the Devices step whenever the
selected Boiler entity does not exist, exactly as it already does for the Climate
Device.

---

## 5. Energy Step

The Energy step shall collect:

### Instantaneous Energy Surplus Entity

Home Assistant entity providing the current available energy surplus.

### Minimum Energy Surplus Entity

Home Assistant entity defining the minimum surplus required before the Climate Device may be used.

---

## 6. Protection Step

The Protection step shall collect:

### Thermostat Tolerance

Temperature hysteresis used by the Demand Engine.

### Shutdown Delay

Minimum time the thermostat remains in STOPPING before requesting the controlled device to stop.

Applies only while the Climate Device is the active heating or cooling solution; never applies while the Boiler is the active heating solution (specs/12_controller_protection_workflow.md §3).

### Source Change Delay

Minimum delay before changing the active heating source.

### Minimum Runtime

Minimum operating time of the currently active heating or cooling solution before it may be stopped or replaced by a different heating source.

---

## 7. Preset Steps

The Configuration Flow shall provide one configuration step for each supported Preset:

- Home
- Away
- Sleep

Every Preset shall expose exactly the same configuration fields.

---

## 8. Heating Target

Desired heating target temperature for the Preset.

---

## 9. Cooling Target

Desired cooling target temperature for the Preset.

---

## 10. Temperature Entity

Home Assistant entity providing the indoor temperature used by the Smart Thermostat while the Preset is active.

The selected entity shall expose a valid numeric temperature value using the configured Home Assistant temperature unit.

The entity may represent, for example:

- a physical temperature sensor;
- a Template Sensor;
- a Helper;
- an aggregated temperature entity;
- any other compatible Home Assistant entity.

The Smart Thermostat never assumes how this value is produced.

---

## 11. Humidity Entity

Optional Home Assistant entity providing the indoor relative humidity used by the Smart Thermostat while the Preset is active.

The selected entity shall expose a valid numeric humidity percentage.

The entity may represent, for example:

- a physical humidity sensor;
- a Template Sensor;
- a Helper;
- an aggregated humidity entity;
- any other compatible Home Assistant entity.

This field is optional.

---

## 12. Validation

The Configuration Flow shall validate that:

- every mandatory entity exists;
- every mandatory entity exposes a compatible value;
- every optional entity, when configured, exposes a compatible value;
- every configured target temperature is valid.

The Configuration Flow shall never validate thermostat behaviour.

---

## 13. Configuration Storage

The Configuration Flow shall persist only user configuration.

The stored configuration shall include:

- General Configuration;
- Device Configuration;
- Energy Configuration;
- Protection Configuration;
- Home Preset Configuration;
- Away Preset Configuration;
- Sleep Preset Configuration.

No calculated or derived values shall be stored.

---

## 14. Runtime Behaviour

Completing the Configuration Flow creates or updates the Config Entry.

The configured values become effective only after the Config Entry has been loaded according to the standard Home Assistant lifecycle.

The Configuration Flow shall never directly control the Smart Thermostat.

---

## 15. Relationship with Presets

The Configuration Flow defines the complete configuration of every Preset.

It does not determine which Preset is active.

The active Preset is selected through the standard Home Assistant Climate Preset Mode interface or through Home Assistant automations.

---

## 16. Architectural Constraints

The Configuration Flow shall never:

- perform thermostat evaluations;
- execute thermostat logic;
- calculate effective target temperatures;
- resolve Temperature Entities;
- resolve Humidity Entities;
- modify Runtime State;
- modify the State Machine.

Its only responsibility is collecting, validating and persisting user configuration.