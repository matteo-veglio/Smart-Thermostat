import dataclasses
import math
from dataclasses import dataclass


@dataclass(frozen=True)
class ClimateControlAlgorithmConfiguration:
    """specs/28_climate_control_mathematical_model.md §6 Configuration Parameters"""

    kp: float
    ti: float
    tt: float
    ts: float
    tac_min: float
    tac_max: float


@dataclass(frozen=True)
class ControllerDiagnosticsSnapshot:
    """Control Diagnostics feature: a passive, immutable record of one controller

    evaluation. This is purely observational - nothing in the mathematical model
    (climate_control_algorithm.py's evaluate()) reads from this snapshot, and
    building/publishing it never alters i_prev, desat_prev, or the returned TAc_Set.
    """

    # Process Variables
    room_temperature: float
    room_target_temperature: float
    climate_device_target_temperature: float  # TAc_Set
    climate_device_internal_temperature: float | None

    # Controller Variables
    control_error: float
    proportional_contribution: float
    integral_contribution: float
    pi_output: float
    feedforward_output: float  # Ytot
    anti_windup_desaturation: float

    # Derived Diagnostics
    feedforward_offset: float
    controller_saturated: bool
    controller_enabled: bool


@dataclass
class ClimateControlAlgorithmState:
    """specs/28_climate_control_mathematical_model.md §7 Persistent Controller State

    `last_valid_output` is not part of the mathematical model's own persistent state
    table; it exists solely so the caller can satisfy §11 ("the previous valid
    controller output shall remain available to the caller"). It is intentionally left
    untouched by reset() - specs/28 §10 defines a reset as resetting exactly i_prev and
    desat_prev, nothing else.

    `last_snapshot` is Control Diagnostics state, not mathematical model state - it is
    likewise never touched by reset() and never read by evaluate()'s calculations.
    """

    i_prev: float = 0.0
    desat_prev: float = 0.0
    last_valid_output: float | None = None
    last_snapshot: ControllerDiagnosticsSnapshot | None = None


class ClimateControlAlgorithm:
    """specs/28_climate_control_mathematical_model.md

    Pure mathematical PI + Feedforward controller with Anti-Windup Back-Calculation.
    Contains no thermostat logic, no Home Assistant logic, no scheduling logic (§12).

    Control Diagnostics (snapshot production) is a passive side observation layered on
    top of this class: it never feeds back into the equations below.
    """

    def __init__(
        self,
        configuration: ClimateControlAlgorithmConfiguration,
        state: ClimateControlAlgorithmState,
        *,
        diagnostics_enabled: bool = False,
    ) -> None:
        self._configuration = configuration
        self._state = state
        self._diagnostics_enabled = diagnostics_enabled

    @property
    def last_output(self) -> float | None:
        return self._state.last_valid_output

    @property
    def last_snapshot(self) -> ControllerDiagnosticsSnapshot | None:
        return self._state.last_snapshot

    def reset(self) -> None:
        # specs/28_climate_control_mathematical_model.md §10 Controller Reset
        self._state.i_prev = 0.0
        self._state.desat_prev = 0.0

    def update_controller_enabled(self, controller_enabled: bool) -> None:
        """Control Diagnostics only: re-stamp the existing snapshot's "Controller

        Enabled" flag so it reflects whether regulation is active *this* evaluation
        cycle, even on cycles where evaluate() was not called (paused/disabled). This
        never recomputes any mathematical value - it only replaces one boolean field on
        an already-computed, immutable snapshot.
        """
        if not self._diagnostics_enabled or self._state.last_snapshot is None:
            return

        self._state.last_snapshot = dataclasses.replace(
            self._state.last_snapshot, controller_enabled=controller_enabled
        )

    def evaluate(
        self,
        *,
        room_target_temperature: float,
        room_temperature: float,
        climate_device_internal_temperature: float | None = None,
    ) -> float | None:
        # specs/28_climate_control_mathematical_model.md §11 Invalid Inputs
        if self._is_invalid(room_target_temperature) or self._is_invalid(room_temperature):
            return self._state.last_valid_output

        cfg = self._configuration

        # Step 1: Err(k) = TRoom_Set(k) - TRoom(k)
        err = room_target_temperature - room_temperature

        # Step 2: P(k) = Kp * Err(k)
        p = cfg.kp * err

        # Step 3: I(k) = I_prev + P(k) * Ts / Ti + Desat_prev * Ts / Tt
        i = self._state.i_prev + p * cfg.ts / cfg.ti + self._state.desat_prev * cfg.ts / cfg.tt

        # Step 4: Y(k) = P(k) + I(k)
        y = p + i

        # Step 5: Ytot(k) = Y(k) + TRoom_Set(k)
        y_tot = y + room_target_temperature

        # Step 6: TAc_Set(k) = max(TAc_min, min(TAc_max, Ytot(k)))
        tac_set = max(cfg.tac_min, min(cfg.tac_max, y_tot))

        # Step 7: Desat(k) = TAc_Set(k) - Ytot(k)
        desat = tac_set - y_tot

        # Step 8: update controller state
        self._state.i_prev = i
        self._state.desat_prev = desat

        self._state.last_valid_output = tac_set

        # Control Diagnostics: a passive observation of the values already computed
        # above. Nothing below this line can affect i_prev, desat_prev or tac_set.
        if self._diagnostics_enabled:
            self._state.last_snapshot = ControllerDiagnosticsSnapshot(
                room_temperature=room_temperature,
                room_target_temperature=room_target_temperature,
                climate_device_target_temperature=tac_set,
                climate_device_internal_temperature=climate_device_internal_temperature,
                control_error=err,
                proportional_contribution=p,
                integral_contribution=i,
                pi_output=y,
                feedforward_output=y_tot,
                anti_windup_desaturation=desat,
                feedforward_offset=tac_set - room_target_temperature,
                controller_saturated=desat != 0.0,
                controller_enabled=True,
            )

        return tac_set

    @staticmethod
    def _is_invalid(value: float | None) -> bool:
        return value is None or math.isnan(value)
