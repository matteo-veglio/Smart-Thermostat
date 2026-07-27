from enum import Enum


class ThermostatState(Enum):
    OFF = "off"
    IDLE = "idle"
    STARTING = "starting"
    HEATING = "heating"
    COOLING = "cooling"
    STOPPING = "stopping"


class InvalidStateTransitionError(Exception):
    def __init__(self, current_state: ThermostatState, target_state: ThermostatState) -> None:
        super().__init__(f"Invalid transition from {current_state} to {target_state}")
        self.current_state = current_state
        self.target_state = target_state


_ALLOWED_TRANSITIONS: dict[ThermostatState, frozenset[ThermostatState]] = {
    ThermostatState.OFF: frozenset({ThermostatState.IDLE}),
    ThermostatState.IDLE: frozenset({ThermostatState.OFF, ThermostatState.STARTING}),
    ThermostatState.STARTING: frozenset(
        {
            ThermostatState.HEATING,
            ThermostatState.COOLING,
            ThermostatState.OFF,
        }
    ),
    ThermostatState.HEATING: frozenset({ThermostatState.STOPPING}),
    ThermostatState.COOLING: frozenset({ThermostatState.STOPPING}),
    ThermostatState.STOPPING: frozenset({ThermostatState.IDLE, ThermostatState.OFF}),
}


class StateMachine:
    def __init__(self, initial_state: ThermostatState) -> None:
        self._current_state = initial_state

    @property
    def current_state(self) -> ThermostatState:
        return self._current_state

    def can_transition_to(self, target_state: ThermostatState) -> bool:
        return target_state in _ALLOWED_TRANSITIONS[self._current_state]

    def transition_to(self, target_state: ThermostatState) -> None:
        if not self.can_transition_to(target_state):
            raise InvalidStateTransitionError(self._current_state, target_state)

        self._current_state = target_state
