# Target Mode

## 1. Purpose

Target Mode defines the source of the target temperatures used by the Smart Thermostat.

The Target Mode determines whether the effective Heating Target and Cooling Target are obtained from the active Preset or from manually configured target temperatures.

The Target Mode is independent of the active Preset.

---

## 2. Supported Target Modes

The Smart Thermostat supports exactly two Target Modes:

- Preset
- Manual

One and only one Target Mode shall always be active.

The Target Mode shall never be undefined.

---

## 3. Preset Target Mode

When the Target Mode is **Preset**, the effective target temperatures shall be obtained from the currently active Preset.

The Runtime Context Factory shall use:

- the active Preset Heating Target;
- the active Preset Cooling Target.

No manual target temperatures shall be considered.

---

## 4. Manual Target Mode

When the Target Mode is **Manual**, the effective target temperatures shall be obtained from the manually configured target temperatures.

The Runtime Context Factory shall use:

- the Manual Heating Target;
- the Manual Cooling Target.

The active Preset remains selected but its target temperatures shall be ignored.

---

## 5. Initial State

When a Smart Thermostat instance is created:

- the active Preset shall be Home;
- the Target Mode shall be Preset.

Consequently:

- the Runtime Context shall initially use the Home Preset target temperatures;
- valid effective target temperatures shall always exist.

### Initial Invariants

After initialization the Smart Thermostat shall always satisfy the following invariants:

- an active Preset always exists;
- an active Target Mode always exists;
- exactly one source of target temperatures is active;
- the Runtime Context always contains valid effective target temperatures;
- the Thermostat Controller never operates without valid target temperatures.

---

## 6. Manual Activation

Manual Target Mode shall be activated automatically whenever the user changes one or both target temperatures through the standard Home Assistant Climate interface.

Examples include:

- `climate.set_temperature`
- Home Assistant Climate Card temperature controls.

Activating Manual Target Mode shall:

- preserve the currently active Preset;
- preserve the complete Preset Configuration;
- update the Manual Heating Target and/or Manual Cooling Target;
- make the Manual target temperatures the active source of target temperatures.

The configured Preset target temperatures shall never be modified by manual target changes.

---

## 7. Manual Target Updates

While Target Mode is **Manual**, every subsequent manual target change shall update the Manual target temperatures.

The Target Mode shall remain **Manual**.

No additional Target Mode transition shall occur.

The active Preset shall remain unchanged.

---

## 8. Preset Activation

Whenever the active Preset changes:

- the Target Mode shall automatically become Preset;
- the effective target temperatures shall immediately become those defined by the newly selected Preset.

The previously configured Manual target temperatures:

- shall remain stored;
- shall no longer affect thermostat operation;
- shall not be modified.

Changing the active Preset always terminates Manual Target Mode.

---

## 9. HVAC Independence

Target Mode and HVAC Mode represent independent concepts.

Changing the Target Mode shall never modify the HVAC Mode.

Changing the HVAC Mode shall never modify the Target Mode.

For example:

- changing the target temperatures while HVAC Mode is OFF shall activate Manual Target Mode without enabling the thermostat;
- enabling the thermostat afterwards shall use the target temperatures determined by the currently active Target Mode.

---

## 10. Runtime Context

The Runtime Context shall never contain:

- the active Preset;
- the Target Mode.

The Runtime Context shall contain only the effective:

- Heating Target;
- Cooling Target.

The Runtime Context Factory shall be solely responsible for resolving the active source of target temperatures into the effective values exposed through the Runtime Context.

---

## 11. Single Source of Target Temperatures

At any instant exactly one source of target temperatures shall be active.

The active source shall be either:

- the currently active Preset;
- the Manual target temperatures.

No thermostat component shall combine target temperatures originating from multiple sources.

No thermostat component shall operate without an active source of target temperatures.

---

## 12. Thermostat Controller

The Thermostat Controller shall never know which Target Mode is active.

The Thermostat Controller shall always operate exclusively on the effective target temperatures contained in the Runtime Context.

No Controller component shall implement Target Mode specific logic.

This includes:

- Demand Engine;
- Source Engine;
- Protection Engine;
- Transition Table;
- Climate Control Table.

---

## 13. Climate Entity

The Climate Entity is responsible for:

- exposing the standard Home Assistant Climate interface;
- storing the active Target Mode;
- storing the Manual Heating Target;
- storing the Manual Cooling Target;
- activating Manual Target Mode after manual target changes;
- activating Preset Target Mode after Preset changes;
- triggering a thermostat evaluation after every Target Mode transition.

The Climate Entity shall never modify the configured Preset target temperatures.

---

## 14. Persistence

Preset Configuration and Manual target temperatures represent different concepts.

Preset Configuration defines persistent comfort profiles.

Manual target temperatures represent temporary runtime user preferences.

These two concepts shall remain completely independent.

The implementation may persist the Manual target temperatures.

The implementation shall never overwrite Preset Configuration with Manual target temperatures.

---

## 15. Architectural Constraints

The Runtime Context Factory shall be the only component responsible for resolving the active source of target temperatures.

The Thermostat Controller shall never determine where target temperatures originate.

The Demand Engine, Source Engine, Protection Engine, Transition Table and Climate Control Table shall always operate exclusively on the effective target temperatures contained in the Runtime Context.

Changing the active Preset shall never modify the Manual target temperatures.

Changing the Manual target temperatures shall never modify the configured Presets.

The active Preset and the Target Mode represent different concepts.

Changing one shall never implicitly modify the other except where explicitly defined by this specification.