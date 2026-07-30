# Options Flow

## 1. Purpose

The Options Flow defines how the configuration of an existing Smart Thermostat instance is modified.

Its only responsibility is allowing the user to update an existing configuration.

It never implements thermostat behaviour.

---

## 2. Relationship with the Configuration Flow

The Options Flow shall expose exactly the same configuration defined by the Configuration Flow.

No additional configuration parameters shall exist.

The Configuration Flow remains the single source of truth for every configurable parameter.

The Options Flow shall always remain functionally equivalent to the Configuration Flow.

---

## 3. Configuration Update

Completing the Options Flow shall update the existing Config Entry.

Only user configuration shall be modified.

No runtime data shall be modified.

No calculated values shall be persisted.

---

## 4. Runtime Behaviour

Updating the configuration through the Options Flow shall not directly control the Smart Thermostat.

After the Config Entry has been updated, the integration shall reload according to the standard Home Assistant lifecycle.

The updated configuration shall become effective only after the reload has completed.

---

## 5. Active Preset

The Options Flow modifies the configuration of every Preset.

It shall never change the currently active Preset.

The active Preset continues to be selected through:

- the Home Assistant Climate Preset Mode interface;
- Home Assistant automations.

---

## 6. Validation

The Options Flow shall perform exactly the same validation rules defined by the Configuration Flow.

No additional validation rules shall exist.

---

## 7. Architectural Constraints

The Options Flow shall never:

- perform thermostat evaluations;
- execute thermostat logic;
- modify Runtime State;
- modify the State Machine;
- calculate effective target temperatures;
- resolve Temperature Entities;
- resolve Humidity Entities.

Its only responsibility is updating user configuration.