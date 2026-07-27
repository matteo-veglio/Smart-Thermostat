from enum import Enum


class Permission(Enum):
    ALLOWED = "allowed"
    DENIED = "denied"


class ProtectionEngine:
    def evaluate_shutdown_delay(
        self,
        now: float,
        demand_ended_at: float,
        shutdown_delay: float,
    ) -> Permission:
        return self._evaluate_elapsed_time(now, demand_ended_at, shutdown_delay)

    def evaluate_source_change_delay(
        self,
        now: float,
        desired_source_differs_since: float,
        source_change_delay: float,
    ) -> Permission:
        return self._evaluate_elapsed_time(now, desired_source_differs_since, source_change_delay)

    def evaluate_minimum_device_runtime(
        self,
        now: float,
        device_started_at: float,
        minimum_device_runtime: float,
    ) -> Permission:
        return self._evaluate_elapsed_time(now, device_started_at, minimum_device_runtime)

    def evaluate_minimum_source_runtime(
        self,
        now: float,
        source_selected_at: float,
        minimum_source_runtime: float,
    ) -> Permission:
        return self._evaluate_elapsed_time(now, source_selected_at, minimum_source_runtime)

    def _evaluate_elapsed_time(
        self,
        now: float,
        reference_timestamp: float,
        required_delay: float,
    ) -> Permission:
        if now - reference_timestamp >= required_delay:
            return Permission.ALLOWED

        return Permission.DENIED
