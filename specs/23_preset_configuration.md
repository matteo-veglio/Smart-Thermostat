# Preset Configuration

## 1. Purpose

A Preset defines a complete comfort profile for the Smart Thermostat.

The active Preset determines the environmental inputs and comfort targets used by the Thermostat Controller.

The Thermostat Controller shall never contain preset-specific logic.

Preset selection is performed externally by Home Assistant automations or by the user through the Climate Entity.

---

## 2. Supported Presets

The Smart Thermostat supports exactly three Presets:

- Home
- Away
- Sleep

The active Preset is exposed through the standard Home Assistant Climate Preset Mode interface.

---

## 3. Preset Configuration

Each Preset contains the following configuration.

### Heating Target

Desired heating temperature.

### Cooling Target

Desired cooling temperature.

### Temperature Entity

Home Assistant entity providing the indoor temperature used by the Smart Thermostat.

The entity:

- shall expose a numeric temperature value;
- shall use the Home Assistant configured temperature unit.

The entity may represent, for example:

- a physical temperature sensor;
- a Template Sensor;
- a Helper;
- an aggregated temperature entity;
- any other Home Assistant entity exposing a valid temperature value.

### Humidity Entity

Optional Home Assistant entity providing the indoor relative humidity.

The entity:

- shall expose a numeric humidity percentage.

The entity may represent:

- a physical humidity sensor;
- a Template Sensor;
- a Helper;
- an aggregated humidity entity;
- any other Home Assistant entity exposing a valid humidity value.

This configuration is optional.

---

## 4. Runtime Context

The Runtime Context shall contain only the effective values of the active Preset.

It shall never contain the Preset itself.

The Runtime Context shall contain:

- current indoor temperature;
- current indoor humidity;
- heating target temperature;
- cooling target temperature.

The Runtime Context Factory is responsible for resolving the active Preset into these effective values.

---

## 5. Thermostat Controller

The Thermostat Controller shall never know which Preset is active.

The Thermostat Controller shall operate exclusively on the Runtime Context.

All thermostat decisions shall therefore remain completely independent of the selected Preset.

---

## 6. Preset Changes

Changing the active Preset shall trigger a complete thermostat evaluation.

The Runtime Context Factory shall immediately use the configuration of the newly selected Preset.

No additional transition rules are introduced.

Changing Preset has the same effect as simultaneously changing:

- heating target;
- cooling target;
- temperature entity;
- humidity entity.

---

## 7. Climate Entity

The Climate Entity exposes the Preset through the standard Home Assistant Climate interface.

The Climate Entity shall not implement any preset-specific logic.

Its responsibility is limited to:

- storing the selected Preset;
- exposing the available Presets;
- triggering a thermostat evaluation after a Preset change.

---

## 8. Architectural Constraints

Preset behaviour shall never be implemented by:

- the Demand Engine;
- the Source Engine;
- the Protection Engine;
- the Transition Table;
- the Climate Control Table.

Preset-specific behaviour is completely resolved before constructing the Runtime Context.

Consequently, every domain component always operates on a fully resolved Runtime Context without knowledge of the active Preset.