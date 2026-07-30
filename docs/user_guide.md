# Smart Thermostat

## User Guide

Version: 1.0

---

# Introduction

Smart Thermostat is a custom Home Assistant integration that provides an intelligent virtual thermostat.

Unlike a traditional thermostat, Smart Thermostat can automatically choose the most appropriate heating source while maintaining a standard Home Assistant Climate interface.

The thermostat has been specifically designed for systems that include:

- a boiler controlled through a relay or dry contact;
- an air conditioner capable of heating and cooling;
- photovoltaic generation.

The integration automatically:

- determines whether heating or cooling is required;
- selects the appropriate heating source;
- regulates the air conditioner using external room temperature sensors;
- minimizes unnecessary compressor and boiler switching.

The user interacts with a normal Home Assistant thermostat.

---

# Features

Smart Thermostat provides:

- Standard Home Assistant Climate Entity.
- Heating and cooling.
- Automatic heating source selection.
- Boiler support.
- Air conditioner support.
- Photovoltaic surplus optimization.
- Configurable thermostat hysteresis.
- Compressor protection.
- Boiler protection.
- Delayed shutdown.
- Source change protection.
- Presets (Away, Home, Sleep).

No custom dashboard cards are required.

---

# Requirements

The integration requires:

- Home Assistant.
- One indoor temperature sensor.
- One optional humidity sensor.
- One boiler controlled by a switch entity.
- One air conditioner exposed as a Climate entity.
- One photovoltaic surplus sensor.
- One configurable minimum surplus value.

---

# Installation

Install the integration using HACS.

Restart Home Assistant.

Add the Smart Thermostat integration from:

Settings

↓

Devices & Services

↓

Add Integration

↓

Smart Thermostat

---

# Configuration

During setup you will be asked to configure:

- Thermostat name.
- Indoor temperature sensor.
- Indoor humidity sensor.
- Boiler switch.
- Air conditioner.
- Instantaneous energy surplus sensor.
- Minimum energy surplus helper.
- Thermostat tolerance.
- Shutdown delay.
- Source change delay.
- Minimum device runtime.
- Minimum source runtime.

---

# Operation

The thermostat supports two HVAC modes.

## Off

The thermostat is disabled.

All controlled devices are turned off.

---

## Heat/Cool

The thermostat automatically determines whether heating or cooling is required.

No manual selection between heating and cooling is necessary.

---

# Presets

The thermostat supports the following presets.

- Away
- Home
- Sleep

Preset changes are managed externally by Home Assistant automations.

---

# Heating Operation

When heating is required, the thermostat automatically chooses between:

- Boiler
- Air Conditioner

The decision depends on the configured photovoltaic surplus.

The selected source is protected against unnecessary switching.

---

# Cooling Operation

Cooling is always performed using the configured air conditioner.

The thermostat regulates the room temperature using the configured indoor temperature sensor.

The internal temperature sensor of the air conditioner is not used for room temperature regulation.

---

# Device Protection

Smart Thermostat includes several protection mechanisms.

These include:

- minimum device runtime;
- delayed shutdown;
- minimum source runtime;
- delayed source switching.

These mechanisms reduce unnecessary compressor and boiler cycling.

---

# Notes

The integration assumes that:

- indoor temperature is already correctly measured;
- photovoltaic surplus is already calculated;
- any temperature averaging is performed outside the integration.

Smart Thermostat intentionally focuses only on thermostat functionality.

---

# Troubleshooting

If the thermostat does not behave as expected:

1. Verify every configured entity exists.
2. Verify the indoor temperature sensor.
3. Verify the surplus sensor.
4. Verify the boiler switch.
5. Verify the air conditioner entity.
6. Enable debug logging if necessary.

---

# Frequently Asked Questions

## Why doesn't the thermostat immediately change heating source?

To prevent unnecessary boiler and compressor switching caused by temporary photovoltaic fluctuations.

---

## Why doesn't the thermostat immediately stop the air conditioner?

To reduce compressor cycling and improve temperature stability.

---

## Why doesn't Smart Thermostat calculate photovoltaic surplus?

Photovoltaic surplus calculation depends on each Home Assistant installation.

The integration expects an already calculated surplus value.

---

## Why doesn't Smart Thermostat average multiple temperature sensors?

Sensor selection and averaging are installation-specific problems.

They are intentionally delegated to Home Assistant template sensors or helper entities.

---

# Support

Before reporting an issue, verify that the behaviour matches the project documentation.

If the behaviour differs from the documented functionality, please include:

- Home Assistant version;
- Smart Thermostat version;
- integration logs;
- configuration details;
- steps required to reproduce the issue.