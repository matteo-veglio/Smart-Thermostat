DOMAIN = "smart_thermostat"

# specs/23_preset_configuration.md §2 Supported Presets
# PRESET_HOME, PRESET_AWAY and PRESET_SLEEP are all standard Home Assistant constants,
# provided by homeassistant.components.climate.

# Historical identifier for the Sleep Preset, replaced by the standard Home Assistant
# PRESET_SLEEP. Kept only as a migration source value - see __init__.py
# async_migrate_entry() and climate.py async_set_preset_mode().
LEGACY_PRESET_NIGHT = "night"


def control_diagnostics_signal(entry_id: str) -> str:
    """Dispatcher signal name used to notify diagnostic sensors of a new snapshot."""
    return f"{DOMAIN}_{entry_id}_control_diagnostics_updated"
