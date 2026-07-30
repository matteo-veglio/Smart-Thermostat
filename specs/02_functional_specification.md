# Smart Thermostat

## Functional Specification

Version: 2.1

Status: Frozen

---

# 1. Purpose

The Smart Thermostat controls the indoor climate of a building.

Its objective is to maintain the requested comfort temperature while optimizing energy usage.

The thermostat may operate using:

- Boiler
- Air Conditioner

The preferred heating source is selected automatically according to the available photovoltaic surplus.

---

# 2. Operating Modes

The thermostat supports the following HVAC modes:

- OFF
- HEAT_COOL

The thermostat shall always operate in exactly one HVAC mode.

OFF disables the thermostat.

While the thermostat is OFF:

- no thermal demand shall be evaluated;
- no Requested Device Actions shall be generated;
- the Thermostat State shall remain OFF.

HEAT_COOL enables the thermostat.

When enabled, the thermostat shall operate according to the normal Thermostat Controller workflow.

The Thermostat Controller shall automatically determine whether heating or cooling is required.

---

# 3. Heating

When the thermostat is enabled, it may request heating.

Heating demand is determined exclusively by the Demand Engine.

The heating source is selected by the Source Engine.

---

# 4. Cooling

When the thermostat is enabled, it may request cooling.

Cooling demand is determined exclusively by the Demand Engine.

Cooling always uses the configured cooling device.

No cooling source selection is performed.

---

# 5. Temperature Control

The thermostat shall regulate room temperature using:

- Heating Target Temperature
- Cooling Target Temperature
- Thermostat Hysteresis

The hysteresis algorithm is defined exclusively in:

- specs/05_control_algorithm.md

---

# 6. Heating Source Selection

Whenever heating demand exists, the thermostat selects one heating source.

Possible heating sources:

- Boiler
- Air Conditioner

The selection algorithm is defined exclusively in:

- specs/06_decision_rules.md

---

# 7. Protection

The thermostat protects connected devices by enforcing:

- Minimum Runtime
- Shutdown Delay
- Source Change Delay

Protection rules are defined exclusively in:

- specs/12_controller_protection_workflow.md

---

# 8. Logical Thermostat State

The thermostat maintains exactly one logical state.

Possible states:

- OFF
- IDLE
- STARTING
- HEATING
- COOLING
- STOPPING

The logical state is managed exclusively by the State Machine.

---

# 9. Runtime Evaluation

For every evaluation cycle:

1. A Runtime Context is created.
2. The Thermostat Controller evaluates the Runtime Context.
3. The Thermostat Controller updates the State Machine if required.
4. The Thermostat Controller updates the Thermostat Runtime State if required.
5. The Thermostat Controller returns the evaluation result.

---

# 10. Heating Source

The thermostat always exposes the currently active heating source.

Possible values:

- Boiler
- Air Conditioner

The current heating source is stored inside the Thermostat Runtime State.

---

# 11. Current Operation

The thermostat always exposes the physical operation currently being performed.

Current Operation is independent from the logical Thermostat State.

Possible values are:

- NONE
- HEATING
- COOLING

Current Operation is produced exclusively by the Thermostat Controller.

The Climate Entity shall never derive the Current Operation.

---

# 12. Availability

The thermostat is available only when every mandatory runtime dependency required for evaluation is available.

Optional runtime values shall never make the thermostat unavailable.

---

# 13. Runtime Context

The Runtime Context is an immutable snapshot created for every evaluation cycle.

It contains:

- Home Assistant runtime information
- Config Entry configuration
- Thermostat Runtime State snapshot

The Runtime Context is discarded after the evaluation completes.

---

# 14. Thermostat Runtime State

The Thermostat Runtime State stores persistent runtime information shared across evaluation cycles.

It survives between evaluations.

It is updated exclusively by the Thermostat Controller.

Its lifecycle is defined in:

- specs/16_runtime_state_management.md

---

# 15. HVAC Action

The Home Assistant HVAC Action represents the physical operation currently being performed by the thermostat.

HVAC Action is exposed exclusively by the Climate Entity.

The Climate Entity SHALL determine the HVAC Action exclusively from the Thermostat Controller Result.

The Climate Entity SHALL NOT derive HVAC Action directly from the Thermostat State.

Possible HVAC Action values are:

- OFF
- IDLE
- HEATING
- COOLING

The Thermostat Controller Result SHALL expose the Current Operation.

Possible Current Operation values are:

- NONE
- HEATING
- COOLING

The Climate Entity SHALL determine the HVAC Action according to the following mapping.

| Thermostat State | Current Operation | HVAC Action |
|------------------|-------------------|-------------|
| OFF | NONE | OFF |
| IDLE | NONE | IDLE |
| STARTING | HEATING | HEATING |
| STARTING | COOLING | COOLING |
| HEATING | HEATING | HEATING |
| COOLING | COOLING | COOLING |
| STOPPING | HEATING | HEATING |
| STOPPING | COOLING | COOLING |

Current Operation represents the physical operation currently being performed.

It is independent from the logical Thermostat State.

The Thermostat Controller is responsible for exposing the Current Operation.

The Climate Entity is responsible only for applying the mapping defined above.

No other HVAC Action mapping shall be implemented.

---

# 16. Responsibilities

The Smart Thermostat domain is divided into specialized components.

| Component | Responsibility |
|-----------|----------------|
| Runtime Context Factory | Build Runtime Context |
| Thermostat Controller | Orchestrate the evaluation |
| State Machine | Maintain logical state |
| Demand Engine | Evaluate thermal demand |
| Source Engine | Select heating source |
| Protection Engine | Evaluate timing constraints |
| Transition Table | Determine requested logical state |
| Device Controllers | Execute physical device commands |

Every component has exactly one responsibility.

No component shall duplicate another component's behaviour.

---

# 17. Source of Truth

This document defines the functional behaviour of the Smart Thermostat.

The detailed implementation rules are defined by the dedicated specification documents.

Every implementation shall strictly follow this specification.