from dataclasses import dataclass

from .demand_engine import Demand, DemandEngine
from .protection_engine import Permission, ProtectionEngine
from .source_engine import HeatingSource, SourceEngine
from .state_machine import StateMachine, ThermostatState
from .transition_table import TransitionTable


@dataclass(frozen=True)
class ThermostatControllerResult:
    demand: Demand
    current_heating_source: HeatingSource
    requested_heating_source: HeatingSource | None
    current_state: ThermostatState
    requested_state: ThermostatState
    protection_result: Permission | None


class ThermostatController:
    def __init__(
        self,
        state_machine: StateMachine,
        demand_engine: DemandEngine,
        source_engine: SourceEngine,
        protection_engine: ProtectionEngine,
        transition_table: TransitionTable,
    ) -> None:
        self._state_machine = state_machine
        self._demand_engine = demand_engine
        self._source_engine = source_engine
        self._protection_engine = protection_engine
        self._transition_table = transition_table

    def evaluate(
        self,
        *,
        current_temperature: float,
        heating_target_temperature: float,
        cooling_target_temperature: float,
        hysteresis: float,
        instantaneous_energy_surplus: float,
        minimum_energy_surplus: float,
        current_heating_source: HeatingSource,
        now: float,
        device_started_at: float,
        minimum_device_runtime: float,
        demand_ended_at: float,
        shutdown_delay: float,
        source_selected_at: float,
        minimum_source_runtime: float,
        desired_source_differs_since: float,
        source_change_delay: float,
    ) -> ThermostatControllerResult:
        current_state = self._state_machine.current_state

        demand = self._demand_engine.evaluate_demand(
            current_temperature=current_temperature,
            heating_target_temperature=heating_target_temperature,
            cooling_target_temperature=cooling_target_temperature,
            hysteresis=hysteresis,
            current_state=current_state,
        )

        protection_result: Permission | None = None
        requested_heating_source: HeatingSource | None = None

        if demand == Demand.HEATING:
            requested_heating_source = self._source_engine.evaluate_source(
                instantaneous_energy_surplus=instantaneous_energy_surplus,
                minimum_energy_surplus=minimum_energy_surplus,
            )

            if requested_heating_source != current_heating_source:
                source_runtime_permission = self._protection_engine.evaluate_minimum_source_runtime(
                    now=now,
                    source_selected_at=source_selected_at,
                    minimum_source_runtime=minimum_source_runtime,
                )

                if source_runtime_permission == Permission.ALLOWED:
                    protection_result = self._protection_engine.evaluate_source_change_delay(
                        now=now,
                        desired_source_differs_since=desired_source_differs_since,
                        source_change_delay=source_change_delay,
                    )
                else:
                    protection_result = source_runtime_permission

        requested_state = self._transition_table.resolve_requested_state(current_state, demand)

        if requested_state != current_state:
            if current_state == ThermostatState.STOPPING and requested_state == ThermostatState.IDLE:
                device_runtime_permission = self._protection_engine.evaluate_minimum_device_runtime(
                    now=now,
                    device_started_at=device_started_at,
                    minimum_device_runtime=minimum_device_runtime,
                )

                if device_runtime_permission == Permission.ALLOWED:
                    protection_result = self._protection_engine.evaluate_shutdown_delay(
                        now=now,
                        demand_ended_at=demand_ended_at,
                        shutdown_delay=shutdown_delay,
                    )
                else:
                    protection_result = device_runtime_permission

                if protection_result == Permission.ALLOWED:
                    self._state_machine.transition_to(requested_state)
            else:
                self._state_machine.transition_to(requested_state)

        return ThermostatControllerResult(
            demand=demand,
            current_heating_source=current_heating_source,
            requested_heating_source=requested_heating_source,
            current_state=self._state_machine.current_state,
            requested_state=requested_state,
            protection_result=protection_result,
        )
