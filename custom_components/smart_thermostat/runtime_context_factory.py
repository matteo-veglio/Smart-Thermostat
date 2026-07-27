from .runtime_context import RuntimeContext
from .state_machine import ThermostatState
from .thermostat_runtime_state import ThermostatRuntimeState


class RuntimeContextFactory:
    def __init__(self, runtime_state: ThermostatRuntimeState) -> None:
        self._runtime_state = runtime_state

    def create(
        self,
        *,
        current_state: ThermostatState,
        current_temperature: float,
        current_humidity: float | None = None,
        heating_target_temperature: float,
        cooling_target_temperature: float,
        hysteresis: float,
        instantaneous_energy_surplus: float,
        minimum_energy_surplus: float,
        now: float,
        minimum_device_runtime: float,
        minimum_source_runtime: float,
        shutdown_delay: float,
        source_change_delay: float,
    ) -> RuntimeContext:
        return RuntimeContext(
            current_state=current_state,
            current_temperature=current_temperature,
            current_humidity=current_humidity,
            heating_target_temperature=heating_target_temperature,
            cooling_target_temperature=cooling_target_temperature,
            hysteresis=hysteresis,
            instantaneous_energy_surplus=instantaneous_energy_surplus,
            minimum_energy_surplus=minimum_energy_surplus,
            current_heating_source=self._runtime_state.current_heating_source,
            current_operation=self._runtime_state.current_operation,
            device_started_at=self._runtime_state.device_started_at,
            demand_ended_at=self._runtime_state.demand_ended_at,
            source_selected_at=self._runtime_state.source_selected_at,
            desired_source_differs_since=self._runtime_state.desired_source_differs_since,
            now=now,
            minimum_device_runtime=minimum_device_runtime,
            minimum_source_runtime=minimum_source_runtime,
            shutdown_delay=shutdown_delay,
            source_change_delay=source_change_delay,
        )
