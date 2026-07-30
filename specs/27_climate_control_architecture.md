# Climate Control Architecture

## 1. Purpose

This specification defines how continuous Climate Device temperature regulation integrates into the Smart Thermostat architecture.

It intentionally does **not** define the mathematical control algorithm.

The mathematical behaviour is defined by:

**28_climate_control_mathematical_model.md**

This document defines only:

- architectural responsibilities;
- execution flow;
- integration points;
- component interactions.

---

# 2. Design Goals

The introduction of continuous Climate Device regulation shall **not** modify the existing Smart Thermostat architecture.

The architecture shall preserve:

- Thermostat Controller responsibilities;
- Demand Engine behaviour;
- Source Engine behaviour;
- Protection Engine behaviour;
- Runtime Context architecture;
- Runtime State architecture;
- Requested Device Actions workflow.

The only new capability introduced by this specification is the continuous regulation of the Climate Device target temperature.

---

# 3. Architectural Principle

The Smart Thermostat continues to operate as a layered decision system.

The architecture is divided into two completely independent responsibilities.

## Decision Layer

Responsible for deciding:

- whether heating is required;
- whether cooling is required;
- which heating source shall be used;
- thermostat state transitions;
- device power requests;
- HVAC mode requests.

## Regulation Layer

Responsible only for determining the optimal Climate Device target temperature.

The Regulation Layer shall never make thermostat decisions.

---

# 4. Separation of Responsibilities

## Thermostat Controller

The Thermostat Controller remains exclusively responsible for:

- demand evaluation;
- state transitions;
- protection evaluation;
- source selection;
- requested device actions.

The Thermostat Controller shall never execute the mathematical control algorithm.

---

## Climate Regulation

Climate regulation is responsible only for continuously calculating the Climate Device target temperature.

It shall never:

- evaluate demand;
- select heating sources;
- evaluate protections;
- generate thermostat state transitions;
- generate device power actions;
- select HVAC mode.

Its sole responsibility is producing the Climate Device target temperature.

---

## Boiler

The Boiler behaviour shall remain completely unchanged.

The mathematical controller shall never be used to regulate the Boiler.

---

# 5. Execution Pipeline

There are now two independent execution flows. See §11 for the full rationale; this
section only describes their shape.

## 5.1 Event-Driven Thermostat Pipeline (unchanged)

Room Temperature / User Command / Entity State Change

↓

Runtime Context Factory

↓

Runtime Context

↓

Thermostat Controller

↓

Requested Device Actions

↓

Climate Device / Boiler

The mathematical controller is **not** executed inside this pipeline. Wherever a
Climate Device target temperature is required, the Thermostat Controller reads the
mathematical controller's most recently produced output (§8) - it never computes a new
one.

## 5.2 Periodic Climate Regulation Pipeline (new)

Dedicated 30-second Scheduler Tick

↓

Latest cached Runtime Context (produced by the pipeline above)

↓

Mathematical Controller Iteration (specs/28)

↓

Event-Driven Thermostat Pipeline (§5.1), to propagate the new output into a
Requested Device Action

This pipeline runs independently of, and asynchronously from, every event listed in
§5.1. It is driven exclusively by elapsed time.

---

# 6. Activation Conditions

Climate Regulation - and therefore its dedicated 30-second scheduler (§11) - is
considered active only when:

- the Climate Device is the active heating source;
- or the thermostat is actively cooling using the Climate Device;

and the thermostat is in the HEATING or COOLING Thermostat State.

Climate Regulation is inactive - and the scheduler shall not be running - when:

- thermostat OFF;
- thermostat IDLE;
- thermostat STARTING;
- thermostat STOPPING;
- Boiler is the active heating source.

This activation decision is still made by the Thermostat Controller, on every
event-driven evaluation (§5.1), exactly as before. It is a passive observation exposed
through the ThermostatControllerResult; computing it never itself executes the
mathematical controller. The Climate Entity acts on it by starting or stopping the
scheduler (§11).

---

# 7. Controller Inputs

The mathematical controller shall never access Home Assistant entities directly.

All required information shall already be available through the Runtime Context and Runtime State.

Typical inputs include:

- effective room target temperature;
- measured room temperature;
- current operating mode;
- controller configuration parameters.

The mathematical controller shall remain completely independent from Home Assistant.

---

# 8. Controller Output

The mathematical controller produces exactly one value.

Climate Device Target Temperature

This value shall be used when generating Climate Device commands.

The controller shall never request:

- HVAC mode changes;
- device power changes;
- thermostat state transitions.

---

# 9. Runtime State

The mathematical controller requires persistent internal state.

The Smart Thermostat shall preserve this state between consecutive evaluations.

The controller state becomes part of the Climate Regulation runtime state.

The Runtime Context shall remain immutable.

---

# 10. Reset Behaviour

The mathematical controller shall be reset only when continuous regulation terminates.

Typical examples include:

- thermostat disabled;
- HVAC OFF;
- transition from Climate Device to Boiler;
- transition from Heating to Cooling;
- transition from Cooling to Heating.

The controller shall never be reset while continuous regulation is still active.

---

# 11. Evaluation Workflow

## 11.1 The event-driven thermostat vs. the periodic Climate Control Algorithm

The Smart Thermostat remains fundamentally event-driven (specs/22_scheduled_evaluation_workflow.md).
The Climate Control Algorithm is the sole, deliberate exception: it is a discrete-time
controller and is therefore evaluated exclusively by a dedicated periodic scheduler
with a fixed 30-second sampling interval, for as long as Climate Regulation is active
(§6). This supersedes the previous language in this section and in
specs/22_scheduled_evaluation_workflow.md §1, which forbade periodic polling
unconditionally; that prohibition now applies to every component of the Smart
Thermostat **except** this one, explicitly scoped exception.

The mathematical controller itself (specs/28) still owns no timer, scheduler, or
asynchronous task - that constraint is unchanged. The scheduler is owned by the Climate
Entity (the Home-Assistant-facing integration layer), which is the only component with
access to Home Assistant's time-tracking helpers. The mathematical model contains no
scheduling logic whatsoever.

## 11.2 Scheduler lifecycle

- When Climate Regulation becomes active (§6): the Climate Entity starts the scheduler
  and immediately executes one complete mathematical controller iteration - identical in
  every respect to a normal scheduled iteration (same method, same effects: controller
  computation, state update, Controller Diagnostics Snapshot, Requested Device Actions,
  diagnostics publication). This eliminates the startup delay that would otherwise leave
  the controller un-executed for up to 30 seconds after activation. This immediate
  execution **is** the first scheduler iteration, not an additional invocation
  mechanism - §11.3's exclusivity guarantee is preserved because it reuses the exact
  same tick method the periodic timer calls, triggered once by the scheduler's own
  startup sequence rather than by any Home Assistant event.
- While Climate Regulation remains active: the scheduler continues to execute exactly
  one mathematical controller iteration every 30 seconds after that immediate one (e.g.
  activation at 12:15:07 -> immediate iteration at 12:15:07, then scheduled iterations at
  12:15:37, 12:16:07, 12:16:37, ...).
- When Climate Regulation stops being active: the Climate Entity stops the scheduler
  immediately. No further iterations occur until it is started again - at which point
  the cycle above (immediate iteration, then 30-second cadence) repeats.
- No controller iterations shall occur while Climate Regulation is inactive.
- The immediate iteration fires at most once per activation: it is gated on the
  scheduler's own not-running -> running transition, so it can never repeat while
  regulation remains continuously active, and never fires at all while regulation stays
  inactive.

## 11.3 Exclusivity

The dedicated 30-second scheduler is the **only** mechanism capable of invoking a
mathematical controller iteration. In particular, none of the following may ever
directly invoke one:

- a service call;
- a Home Assistant entity state change (room temperature, energy sensors, Boiler,
  Climate Device, or any other tracked entity);
- an HVAC mode change;
- a preset change;
- a Manual Target Mode change;
- a Runtime Context update;
- a Thermostat State transition;
- a heating/cooling source change;
- a Protection Engine decision;
- the one-shot Scheduled Evaluation Workflow (specs/22_scheduled_evaluation_workflow.md);
- any other Home Assistant event, callback, or listener.

All of the above may freely cause the Runtime Context to be recomputed (they remain
fully event-driven, unchanged) - and the scheduler's next tick will read whichever
Runtime Context is freshest at that moment - but none of them execute the mathematical
controller themselves.

## 11.4 Scheduler inputs

On every tick, the scheduler reads the most recently resolved Runtime Context - produced
by the ordinary event-driven Thermostat Pipeline (§5.1) as events occur - rather than
deriving or fetching anything itself. It never re-implements Target Mode or Preset
resolution; that remains the sole responsibility of the Runtime Context Factory
(specs/13_runtime_context.md, §13 below).

## 11.5 Propagating the result

A mathematical controller iteration only produces a new Climate Device target
temperature (§8); it never generates a Requested Device Action itself (§15). Immediately
after each iteration, the scheduler triggers one ordinary event-driven Thermostat
Pipeline evaluation (§5.1), which reads the controller's now-updated output (§8) and
generates the corresponding Requested Device Action, if the rounded, de-duplicated value
actually changed. This propagation step performs no mathematical controller iteration of
its own - by the time it runs, the iteration has already happened.

---

# 12. Configuration

The mathematical controller parameters become part of the Smart Thermostat configuration.

At minimum the following parameters shall be configurable:

- Proportional Gain (Kp)
- Integral Time (Ti)
- Tracking Time (Tt)
- Minimum Climate Temperature
- Maximum Climate Temperature

The controller shall never contain hardcoded tuning values.

---

# 13. Interaction with Runtime Context

The Runtime Context Factory continues resolving:

- active preset;
- target mode;
- effective heating target;
- effective cooling target.

The mathematical controller receives only already-resolved target temperatures.

It shall never know:

- presets;
- target mode;
- Home Assistant entities.

---

# 14. Interaction with Protection Engine

The Protection Engine shall execute before Climate Regulation.

Protection decisions always take precedence over continuous regulation.

The mathematical controller shall never bypass:

- Shutdown Delay;
- Minimum Runtime;
- Source Change Delay.

---

# 15. Device Actions

Requested Device Actions remain generated by the Thermostat Controller.

The mathematical controller shall never create new actions.

Its only contribution is determining the target temperature associated with Climate Device actions.

---

# 16. Architectural Constraints

The mathematical controller shall never become a second Thermostat Controller.

It shall never:

- evaluate thermostat demand;
- decide thermostat state;
- select heating source;
- select cooling source;
- select HVAC mode;
- generate device actions;
- evaluate protection logic.

The controller is exclusively responsible for continuous Climate Device regulation.

---

# 17. Architectural Invariants

After implementation the following statements shall always remain true.

- Thermostat Controller behaviour is unchanged.
- Demand Engine behaviour is unchanged.
- Source Engine behaviour is unchanged.
- Protection Engine behaviour is unchanged.
- Boiler behaviour is unchanged.
- Runtime Context architecture is unchanged.
- Requested Device Actions architecture is unchanged.
- The mathematical controller has exactly one responsibility:
  calculating the Climate Device target temperature.
- The mathematical controller is evaluated exclusively by its dedicated 30-second
  scheduler (§11), and by no other mechanism.
- The event-driven Smart Thermostat (Thermostat Controller, Demand Engine, Source
  Engine, Protection Engine, State Machine) remains completely event-driven; the
  Climate Control Algorithm is the only periodic exception.

---

# 18. Compliance

Any implementation claiming compliance with this specification shall satisfy all of the following:

- preserve the existing Smart Thermostat architecture;
- integrate the mathematical controller without duplicating thermostat logic;
- maintain strict separation between decision making and continuous regulation;
- preserve single responsibility for every existing component;
- comply completely with all previously frozen Smart Thermostat specifications.