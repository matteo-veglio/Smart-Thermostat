from dataclasses import dataclass
from enum import Enum


class PowerState(Enum):
    ON = "on"
    OFF = "off"


class ClimateHVACMode(Enum):
    HEAT = "heat"
    COOL = "cool"


@dataclass(frozen=True)
class TurnBoilerOn:
    pass


@dataclass(frozen=True)
class TurnBoilerOff:
    pass


@dataclass(frozen=True)
class TurnClimateOn:
    pass


@dataclass(frozen=True)
class TurnClimateOff:
    pass


@dataclass(frozen=True)
class SetClimateHVACMode:
    hvac_mode: ClimateHVACMode


@dataclass(frozen=True)
class SetClimateTargetTemperature:
    target_temperature: float


DeviceAction = (
    TurnBoilerOn
    | TurnBoilerOff
    | TurnClimateOn
    | TurnClimateOff
    | SetClimateHVACMode
    | SetClimateTargetTemperature
)
