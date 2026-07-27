# Smart Thermostat

## Climate Control Table Configuration

Version: 1.0

Status: Frozen

---

# 1. Purpose

This document defines how the Climate Control Table is configured.

The configuration defines only the table values.

The evaluation algorithm is defined exclusively by:

- specs/19_climate_control_table.md

Changing the configuration shall never modify the evaluation algorithm.

---

# 2. Responsibilities

The configuration SHALL define:

- the Heating Control Table;
- the Cooling Control Table.

The configuration SHALL NOT define:

- evaluation logic;
- interpolation rules;
- thermostat algorithms.

---

# 3. Heating Control Table

The Heating Control Table is an ordered list of entries.

Each entry contains:

- Minimum Temperature Error
- Maximum Temperature Error
- Requested Climate Target Temperature

The entries SHALL cover the complete supported temperature error range.

The entries SHALL NOT overlap.

Exactly one entry SHALL match every temperature error.

---

# 4. Cooling Control Table

The Cooling Control Table follows the same structure as the Heating Control Table.

The entries SHALL cover the complete supported temperature error range.

The entries SHALL NOT overlap.

Exactly one entry SHALL match every temperature error.

---

# 5. Validation

During configuration loading the Smart Thermostat SHALL validate:

- every table is ordered;
- no entries overlap;
- no gaps exist;
- every requested climate target temperature is valid.

If validation fails the configuration SHALL be rejected.

---

# 6. Runtime Behaviour

The Climate Control Table configuration is read-only during runtime.

The Thermostat Controller SHALL never modify it.

The Runtime Context SHALL expose the loaded configuration when required for evaluation.

---

# 7. Defaults

The Smart Thermostat SHALL provide a default Heating Control Table and a default Cooling Control Table.

Users may replace the default values through configuration.

Changing the values shall not require code changes.

---

# 8. Independence

The Climate Control Table configuration belongs to the Smart Thermostat domain.

It is independent from:

- Home Assistant;
- Climate integrations;
- Device manufacturers.

---

# 9. Source of Truth

This document defines the configuration of the Climate Control Table.

Every implementation shall strictly follow this specification.