# Smart Thermostat

## State Machine

Version: 1.0

Status: Frozen

---

# 1. Purpose

This document defines the internal operating state machine of the Smart Thermostat.

The state machine describes every possible operating state and the allowed transitions between them.

Algorithms used to trigger transitions are intentionally excluded.

---

# 2. Objectives

The state machine shall:

- define the operating behaviour of the thermostat;
- guarantee deterministic behaviour;
- avoid undefined states;
- protect physical devices from excessive switching;
- provide a single source of truth for the internal operating state.

---

# 3. State Machine

The thermostat is modelled as the following finite state machine.

```
                     OFF
                      │
          HVAC Mode = Heat/Cool
                      │
                      ▼
                    IDLE
                   ╱ │ ╲
                  ╱  │  ╲
                 ▼   ▼   ▼
           STARTING STARTING STARTING
              │        │        │
              ▼        ▼        ▼
     HEATING_BOILER HEATING_AC COOLING_AC
             │            │          │
             ▼            ▼          ▼
     DELAY_OFF_HEATING    │   DELAY_OFF_COOLING
             │            │          │
             └────────────┴──────────┘
                      │
                      ▼
                     IDLE
```

---

# 4. States

## OFF

### Description

The thermostat is disabled.

### Responsibilities

- No thermal demand is evaluated.
- All controlled devices are turned off.
- The control cycle remains active.
- The thermostat waits for HVAC mode changes.

### Allowed Transitions

- OFF → IDLE

---

## IDLE

### Description

The thermostat is enabled but no thermal demand currently exists.

### Responsibilities

- Evaluate thermal demand.
- Wait for heating or cooling requests.

### Allowed Transitions

- IDLE → STARTING
- IDLE → OFF

---

## STARTING

### Description

The thermostat has determined that a new operating cycle must begin.

The selected operating strategy is prepared before entering normal operation.

### Responsibilities

- Determine the selected operating strategy.
- Prepare the selected device.
- Configure the selected device.
- Configure the initial operating parameters.
- Verify that the system is ready for normal operation.

### Allowed Transitions

- STARTING → HEATING_BOILER
- STARTING → HEATING_AC
- STARTING → COOLING_AC
- STARTING → OFF

---

## HEATING_BOILER

### Description

Heating demand is active.

The boiler is the selected heating source.

### Responsibilities

- Maintain heating operation.
- Continuously evaluate thermostat conditions.
- Continuously evaluate source selection conditions.

### Allowed Transitions

- HEATING_BOILER → DELAY_OFF_HEATING
- HEATING_BOILER → STARTING
- HEATING_BOILER → OFF

---

## HEATING_AC

### Description

Heating demand is active.

The air conditioner is the selected heating source.

### Responsibilities

- Maintain heating operation.
- Continuously regulate the HVAC target temperature.
- Continuously evaluate thermostat conditions.
- Continuously evaluate source selection conditions.

### Allowed Transitions

- HEATING_AC → DELAY_OFF_HEATING
- HEATING_AC → STARTING
- HEATING_AC → OFF

---

## DELAY_OFF_HEATING

### Description

Heating demand has ended.

The active heating source remains enabled during the shutdown delay.

### Responsibilities

- Wait for the shutdown delay.
- Allow heating demand recovery.
- Prevent unnecessary switching of the heating device.

### Allowed Transitions

- DELAY_OFF_HEATING → HEATING_BOILER
- DELAY_OFF_HEATING → HEATING_AC
- DELAY_OFF_HEATING → IDLE
- DELAY_OFF_HEATING → OFF

---

## COOLING_AC

### Description

Cooling demand is active.

The air conditioner is operating in cooling mode.

### Responsibilities

- Maintain cooling operation.
- Continuously regulate the HVAC target temperature.
- Continuously evaluate thermostat conditions.

### Allowed Transitions

- COOLING_AC → DELAY_OFF_COOLING
- COOLING_AC → OFF

---

## DELAY_OFF_COOLING

### Description

Cooling demand has ended.

The air conditioner remains enabled during the shutdown delay.

### Responsibilities

- Wait for the shutdown delay.
- Allow cooling demand recovery.
- Prevent unnecessary compressor cycling.

### Allowed Transitions

- DELAY_OFF_COOLING → COOLING_AC
- DELAY_OFF_COOLING → IDLE
- DELAY_OFF_COOLING → OFF

---

# 5. Events

The following events may trigger state transitions.

- HVAC Mode Changed
- Heating Request Started
- Heating Request Ended
- Cooling Request Started
- Cooling Request Ended
- Heating Source Changed
- Shutdown Delay Expired

The algorithms generating these events are defined in the Control Algorithm specification.

---

# 6. Transition Rules

A transition shall occur only when:

- the current state allows it;
- the triggering event is valid;
- all protection rules are satisfied.

Transitions shall never bypass intermediate states.

---

# 7. Forbidden Transitions

The following transitions are not allowed.

- OFF → HEATING_BOILER
- OFF → HEATING_AC
- OFF → COOLING_AC
- HEATING_BOILER → COOLING_AC
- HEATING_AC → COOLING_AC
- COOLING_AC → HEATING_BOILER
- COOLING_AC → HEATING_AC
- DELAY_OFF_HEATING → COOLING_AC
- DELAY_OFF_COOLING → HEATING_BOILER
- DELAY_OFF_COOLING → HEATING_AC

Heating and cooling shall never change directly.

The thermostat shall always return to IDLE before switching between heating and cooling.

---

# 8. State Persistence

The current operating state shall always be stored internally.

After a Home Assistant restart, the thermostat shall restore the previous valid operating state whenever possible.

If restoration is not possible, the thermostat shall initialize according to the configured HVAC mode.

---

# 9. Source of Truth

This document is the authoritative definition of the Smart Thermostat internal state machine.

No additional operating states shall exist outside this specification.

Any modification of the operating states requires an explicit update of this document.