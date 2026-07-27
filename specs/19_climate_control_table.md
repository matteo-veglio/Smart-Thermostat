# Smart Thermostat

## Climate Control Table

Version: 1.0

Status: Frozen

---

# 1. Purpose

This document defines how the Smart Thermostat determines the target temperature requested from a Climate Device.

The Smart Thermostat shall never send the user target temperature directly to a Climate Device.

Instead, the requested climate target temperature shall be determined using a Climate Control Table.

The Climate Control Table is part of the Smart Thermostat domain.

---

# 2. Responsibilities

The Climate Control Table SHALL:

- receive the current operating mode;
- receive the current room temperature;
- receive the user target temperature;
- determine the requested Climate Device target temperature.

The Climate Control Table SHALL NOT:

- evaluate thermal demand;
- select the heating source;
- communicate with Home Assistant;
- execute Device Actions.

---

# 3. Inputs

The Climate Control Table receives:

- Current Operation
- Current Room Temperature
- User Heating Target Temperature
- User Cooling Target Temperature

The appropriate target temperature depends on the current operation.

---

# 4. Temperature Error

The temperature error SHALL be calculated as follows.

## Heating

Temperature Error = Heating Target Temperature − Current Room Temperature

## Cooling

Temperature Error = Current Room Temperature − Cooling Target Temperature

A positive temperature error always represents additional thermal demand.

---

# 5. Table Structure

The Climate Control Table is an ordered collection of entries.

Each entry defines:

- Minimum Temperature Error
- Maximum Temperature Error
- Requested Climate Target Temperature

Exactly one entry SHALL match every temperature error.

---

# 6. Heating Table

When Current Operation is HEATING, the Heating Table SHALL be used.

The Heating Table converts the heating temperature error into the requested Climate Device target temperature.

The exact table values are configuration parameters.

The evaluation algorithm shall remain identical regardless of the configured values.

---

# 7. Cooling Table

When Current Operation is COOLING, the Cooling Table SHALL be used.

The Cooling Table converts the cooling temperature error into the requested Climate Device target temperature.

The exact table values are configuration parameters.

The evaluation algorithm shall remain identical regardless of the configured values.

---

# 8. Evaluation

For every thermostat evaluation:

1. Calculate the temperature error.
2. Select the appropriate Climate Control Table.
3. Find the matching table entry.
4. Produce exactly one requested Climate Device target temperature.

The evaluation SHALL always produce one deterministic result.

---

# 9. Requested Device Actions

Whenever the Thermostat Controller generates a Set Climate Target Temperature action, the requested temperature SHALL be the result produced by the Climate Control Table.

The user target temperature shall never be sent directly to the Climate Device.

---

# 10. Device Independence

The Climate Control Table belongs to the Smart Thermostat domain.

It is independent from:

- Home Assistant;
- Climate integrations;
- Device manufacturers.

Every Climate Device shall receive the requested target temperature produced by the same Climate Control Table.

---

# 11. Source of Truth

This document defines the Climate Control Table used by the Smart Thermostat.

Every implementation shall strictly follow this specification.