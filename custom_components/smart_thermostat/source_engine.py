from enum import Enum


class HeatingSource(Enum):
    BOILER = "boiler"
    AIR_CONDITIONER = "air_conditioner"


class SourceEngine:
    def evaluate_source(
        self,
        instantaneous_energy_surplus: float,
        minimum_energy_surplus: float,
    ) -> HeatingSource:
        if instantaneous_energy_surplus >= minimum_energy_surplus:
            return HeatingSource.AIR_CONDITIONER

        return HeatingSource.BOILER
