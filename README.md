# Smart Thermostat

Smart Thermostat is a custom Home Assistant integration that provides an intelligent virtual thermostat for homes equipped with multiple heating sources.

The integration automatically manages heating and cooling while selecting the most appropriate heating source according to the available photovoltaic surplus.

Unlike traditional thermostats, Smart Thermostat regulates the room temperature using external temperature sensors instead of relying on the internal sensors of the air conditioner.

---

## Features

- Standard Home Assistant Climate Entity
- Heating and Cooling
- Automatic heating source selection
- Boiler support
- Air conditioner support
- Photovoltaic surplus optimization
- Configurable thermostat hysteresis
- Compressor protection
- Boiler protection
- Delayed shutdown
- Delayed heating source switching
- Presets (Away, Home, Night)

---

## Supported System

Smart Thermostat is designed for installations including:

- Home Assistant
- Boiler controlled through a switch
- Air conditioner exposed as a Climate entity
- Indoor temperature sensor
- Indoor humidity sensor (optional)
- Photovoltaic surplus sensor

---

## Documentation

### User Documentation

- docs/user_guide.md

### Project Specifications

The complete software specification is available inside the `specs` directory.

The specification is divided into the following documents:

1. Project Overview
2. Functional Specification
3. Software Architecture
4. State Machine
5. Control Algorithm
6. Decision Rules
7. Configuration
8. LLM Development Guidelines
9. Development Tasks

---

## Installation

Installation instructions will be available after the first public release.

---

## Development

The project follows a documentation-first approach.

Every implementation task is driven by the project specifications.

The documentation is considered the single source of truth.

---

## License

This project is released under the MIT License.