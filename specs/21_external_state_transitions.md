# Smart Thermostat

## External State Transitions

Version: 1.0

Status: Frozen

---

# 1. Purpose

This document defines how external user actions interact with the Thermostat State Machine.

The Thermostat State Machine models only the internal operating behaviour of the thermostat.

External user actions are not part of the State Machine transition table.

Instead, they initiate or terminate the thermostat operating lifecycle.

---

# 2. Responsibilities

External user actions SHALL:

- enable the thermostat;
- disable the thermostat.

The Thermostat Controller SHALL continue to manage every internal state transition.

---

# 3. Enabling the Thermostat

When the user changes the Home Assistant HVAC Mode from OFF to an operational mode, the thermostat becomes enabled.

If the current Thermostat State is OFF, the following transition SHALL occur immediately:

```
OFF
    ↓
IDLE
```

No Demand evaluation is required before this transition.

No Protection rules are evaluated.

No Requested Device Actions are generated.

This transition represents only that the thermostat is now allowed to begin normal operation.

The next evaluation cycle SHALL determine whether the thermostat remains in IDLE or progresses to STARTING according to the normal Thermostat Controller workflow.

---

# 4. Disabling the Thermostat

When the user changes the Home Assistant HVAC Mode to OFF, the thermostat becomes disabled.

The requested thermostat state becomes OFF.

The Thermostat Controller SHALL determine how to reach OFF according to the normal controller workflow.

If the thermostat is already IDLE, the transition to OFF may occur immediately.

If the thermostat is STARTING, HEATING, COOLING or STOPPING, the controller SHALL respect every protection rule before reaching OFF.

The Climate Entity SHALL NOT bypass the Thermostat Controller.

---

# 5. Separation of Responsibilities

The Climate Entity is responsible only for forwarding external user requests.

The Climate Entity SHALL NOT:

- evaluate Demand;
- evaluate Protection;
- determine Requested Device Actions;
- bypass the State Machine.

The Thermostat Controller remains responsible for all internal thermostat behaviour.

---

# 6. Relationship with the State Machine

The State Machine defined in specs/04_state_machine.md models only the internal operating lifecycle.

The Transition Table defined in specs/11_controller_transition_table.md applies only while the thermostat is enabled.

Transitions caused directly by external user actions are defined exclusively by this document.

---

# 7. Source of Truth

This document defines how external user actions interact with the Thermostat State Machine.

Every implementation shall strictly follow this specification.