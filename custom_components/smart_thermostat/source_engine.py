from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .runtime_context import RuntimeContext


class HeatingSource(Enum):
    BOILER = "boiler"
    AIR_CONDITIONER = "air_conditioner"


class SourceEngine:
    def evaluate_source(self, context: RuntimeContext) -> HeatingSource:
        if context.instantaneous_energy_surplus >= context.minimum_energy_surplus:
            return HeatingSource.AIR_CONDITIONER

        return HeatingSource.BOILER
