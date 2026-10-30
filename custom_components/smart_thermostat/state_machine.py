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
            # specs/11_controller_transition_table.md §7: if the startup request is
            # cancelled before completion (demand disappears before HEATING/COOLING is
            # confirmed), the requested state becomes IDLE. specs/12_controller_
            # protection_workflow.md §3 documents that this uses the same protection
            # model as STOPPING -> IDLE, since the Climate Device may already have been
            # commanded on during STARTING.
            ThermostatState.IDLE,
        }
    ),
    ThermostatState.HEATING: frozenset({ThermostatState.STOPPING}),
    ThermostatState.COOLING: frozenset({ThermostatState.STOPPING}),
    # specs/04_state_machine.md §4 / specs/11_controller_transition_table.md §8: STOPPING
    # represents a shutdown that has been decided but not yet executed - the controlled
    # device is still physically active throughout. If demand returns before the
    # shutdown completes, the pending shutdown is cancelled and the thermostat resumes
    # through STARTING, without ever passing through IDLE.
    ThermostatState.STOPPING: frozenset(
        {ThermostatState.IDLE, ThermostatState.OFF, ThermostatState.STARTING}
    ),
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

    def restore_state(self, state: ThermostatState) -> None:
        # specs/29_restart_recovery.md §3: set the current state directly, bypassing
        # transition validation. Used exclusively once, during startup restoration,
        # before any evaluation has ever run against this instance - restoring a
        # prior process's last state is not itself a demand-driven transition and is
        # therefore intentionally exempt from _ALLOWED_TRANSITIONS. Never call this
        # outside of startup restoration; every other state change must continue to
        # go through transition_to().
        self._current_state = state
