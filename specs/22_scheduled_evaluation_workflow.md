# Scheduled Evaluation Workflow

## 1. Purpose

The Smart Thermostat is fundamentally event-driven.

Thermostat evaluations normally occur only after external events, including:

- User commands.
- Sensor state changes.
- Controlled device state changes.

However, some Protection Rules depend exclusively on elapsed time.

Examples include:

- Shutdown Delay.
- Minimum Runtime.
- Source Change Delay.

These protection conditions may become satisfied without any external event occurring.

The architecture shall therefore support scheduled one-shot thermostat evaluations.

Periodic polling is explicitly forbidden for thermostat decision making - that is, for
the Thermostat Controller, the Demand Engine, the Source Engine, the Protection Engine,
and the State Machine. All thermostat evaluations governed by this document remain
event-driven or one-shot scheduled, exactly as described below.

### 1.1 Exception: the Climate Control Algorithm

The Climate Control Algorithm (the PI + Feedforward + Anti-windup mathematical
controller, see specs/27_climate_control_architecture.md and
specs/28_climate_control_mathematical_model.md) is a deliberate, explicitly scoped
exception to the event-driven principle above.

It is a discrete-time controller and is therefore evaluated exclusively by its own
dedicated periodic scheduler with a fixed 30-second sampling interval, for as long as
Climate Regulation is active. This periodic execution model applies **only** to the
Climate Control Algorithm's own evaluation. It does not reintroduce polling anywhere
else: the Thermostat Controller and every component listed above remain fully
event-driven, exactly as the rest of this document describes.

specs/27_climate_control_architecture.md §11 defines this scheduler's behaviour in
full. Nothing else in this document - the one-shot scheduled evaluation workflow below -
is affected by this exception.

---

## 2. Thermostat Controller Responsibility

The Thermostat Controller remains the only component responsible for thermostat decision making.

Whenever a requested Thermostat State transition is denied exclusively by one or more Protection Rules whose outcome depends only on elapsed time, the Thermostat Controller shall determine the earliest instant at which another evaluation may produce a different decision.

Additionally, whenever the Thermostat Controller transitions from:

- HEATING → STOPPING
- COOLING → STOPPING

it shall request one immediate follow-up evaluation.

This immediate follow-up evaluation is required because the Protection Rules governing the STOPPING → IDLE transition are evaluated only while the current Thermostat State is already STOPPING.

The Thermostat Controller shall expose all evaluation requests through the ThermostatControllerResult.

The Thermostat Controller shall never perform scheduling itself.

---

## 3. ThermostatControllerResult

ThermostatControllerResult shall expose optional scheduling information.

The scheduling information may represent either:

- an immediate follow-up evaluation;
- a delayed evaluation after a remaining protection delay.

If no further evaluation is required, no scheduling information shall be provided.

The ThermostatControllerResult shall never schedule evaluations itself.

---

## 4. Climate Entity Responsibility

After every thermostat evaluation, the Climate Entity shall inspect the ThermostatControllerResult.

If no scheduling information is present:

- no callback shall be scheduled.

If an immediate evaluation is requested:

- no callback shall be created;
- one additional async_evaluate() shall be executed immediately.

If a delayed evaluation is requested:

- any previously scheduled callback shall be cancelled;
- exactly one one-shot callback shall be scheduled;
- the callback shall invoke async_evaluate() exactly once.

The Climate Entity shall never determine whether another evaluation is required.

It shall only execute the scheduling requested by the Thermostat Controller.

---

## 5. Delayed Evaluations

Whenever a delayed evaluation is requested, the remaining delay shall represent the earliest instant at which another thermostat evaluation may produce a different controller decision.

The scheduling mechanism shall never wake earlier than required.

---

## 6. Callback Replacement

Only one scheduled evaluation may exist at any time.

Whenever a new thermostat evaluation occurs before the scheduled callback executes:

- the pending callback shall be cancelled;
- the latest ThermostatControllerResult shall be inspected;
- a new callback may be scheduled if required.

---

## 7. External Events

Any external event that already triggers a thermostat evaluation shall also cancel any pending scheduled evaluation.

After the new evaluation completes, scheduling shall be recomputed from the latest ThermostatControllerResult.

---

## 8. Architectural Constraints

The scheduling mechanism shall never:

- perform periodic polling;
- execute thermostat decision logic;
- modify Runtime State;
- modify the State Machine;
- bypass the Thermostat Controller;
- bypass the Protection Engine.

The Thermostat Controller remains the only component responsible for deciding whether another evaluation is required.

The Climate Entity remains responsible only for executing evaluations and scheduling the requested follow-up evaluation.

---

## 9. Evaluation Sources

A thermostat evaluation may only be be triggered by one of the following sources:

- User command.
- External entity state change.
- Immediate follow-up evaluation requested by the Thermostat Controller.
- Scheduled one-shot evaluation requested by the Thermostat Controller.
- Climate Regulation tick: the propagation step that follows a periodic Climate Control
  Algorithm iteration (specs/27_climate_control_architecture.md §11). This source never
  triggers a PI iteration itself - the iteration has already occurred, directly, an
  instant earlier, driven exclusively by the dedicated 30-second scheduler. This
  evaluation only propagates the already-computed output into a Requested Device Action.

No other evaluation source shall exist.

The immediate follow-up evaluation shall execute at most once for each transition into STOPPING