# Smart Thermostat

## Project Overview

Version: 1.0

Status: Frozen

---

# 1. Purpose

Smart Thermostat is a custom Home Assistant integration that implements an intelligent virtual thermostat.

The integration exposes a standard Home Assistant Climate Entity while internally managing multiple heating and cooling sources according to configurable control algorithms.

The primary objective is to maximize thermal comfort while automatically selecting the most appropriate heating source based on real-time energy availability.

The integration is designed to compensate for the poor temperature regulation typically found in residential air conditioners by using external room temperature sensors instead of the internal sensors built into the HVAC units.

---

# 2. Goals

The integration shall:

- Expose a standard Home Assistant Climate Entity.
- Provide an interface familiar to Home Assistant users.
- Automatically determine when heating or cooling is required.
- Automatically select the most appropriate heating source.
- Support photovoltaic surplus optimization.
- Reduce unnecessary device switching.
- Reduce compressor start/stop cycles.
- Improve room temperature stability.
- Be fully configurable through Home Assistant Config Flow.
- Operate without requiring custom Lovelace cards.

---

# 3. Project Philosophy

The integration must hide all internal complexity from the user.

The user interacts with a normal thermostat.

The integration internally manages:

- demand calculation;
- source selection;
- proportional HVAC control;
- shutdown delays;
- source switching;
- compressor protection;
- energy optimization.

The user never manually selects which heating source should be used.

---

# 4. Scope

The project implements only thermostat logic.

The integration is responsible for:

- evaluating thermal demand;
- selecting the heating source;
- controlling the selected device;
- exposing a Climate Entity.

The integration is not responsible for:

- photovoltaic production calculations;
- surplus calculations;
- temperature averaging;
- sensor selection;
- presence detection;
- automatic preset changes;
- energy management.

These functions must be implemented using native Home Assistant helpers, template sensors or automations.

---

# 5. Design Principles

The project follows the following principles.

## Simplicity

Every component has a single responsibility.

## Predictability

The thermostat shall always behave deterministically.

The same inputs must always generate the same outputs.

## Stability

The integration shall avoid unnecessary state changes.

The protection of physical devices has priority over fast reactions.

## Modularity

Every subsystem shall be independent from the others.

Each subsystem must be individually testable.

## Native Home Assistant

The integration shall follow Home Assistant architecture and conventions.

No custom frontend components are required.

---

# 6. Supported Features

The first version of the integration supports:

- Heating.
- Cooling.
- Automatic heating/cooling mode.
- Boiler control.
- Air conditioner control.
- Automatic heating source selection.
- Photovoltaic surplus optimization.
- Preset support.
- External temperature sensor.
- External humidity sensor.

---

# 7. Unsupported Features

The first version intentionally excludes:

- PID controllers.
- Weather prediction.
- Self-learning algorithms.
- AI-based control.
- Multiple simultaneous heating sources.
- Multi-zone control.
- Scheduling.
- Presence detection.
- Automatic preset management.

These features may be evaluated in future releases but are outside the scope of Version 1.

---

# 8. Documentation Structure

Project documentation is divided into independent documents.

Each document owns a single topic.

Information shall never be duplicated across documents.

The documentation is organized as follows:

01_project_overview.md

General description of the project.

02_functional_specification.md

Functional behaviour of the thermostat.

03_architecture.md

Software architecture.

04_state_machine.md

Internal state machine.

05_control_algorithm.md

Heating and cooling control algorithms.

06_configuration.md

Configuration parameters.

07_entities.md

Home Assistant entities and services.

08_development_guidelines.md

Development rules.

09_roadmap.md

Future evolution of the project.

---

# 9. Development Process

The project follows a documentation-first approach.

The development workflow is:

1. Define requirements.
2. Freeze documentation.
3. Review documentation.
4. Create development tasks.
5. Implement code.
6. Test.
7. Release.

Implementation must never anticipate features that are not explicitly defined in the documentation.

---

# 10. Documentation Policy

Once approved, every document is considered frozen.

Changes are allowed only through an explicit documentation update.

The implementation must always follow the documentation.

The documentation is the single source of truth for the project.