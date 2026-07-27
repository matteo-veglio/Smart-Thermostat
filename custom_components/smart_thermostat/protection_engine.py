from enum import Enum

from .runtime_context import RuntimeContext


class Permission(Enum):
    ALLOWED = "allowed"
    DENIED = "denied"


class ProtectionEngine:
    def evaluate_shutdown_delay(self, context: RuntimeContext) -> Permission:
        return self._evaluate_elapsed_time(context.now, context.demand_ended_at, context.shutdown_delay)

    def evaluate_source_change_delay(self, context: RuntimeContext) -> Permission:
        return self._evaluate_elapsed_time(
            context.now, context.desired_source_differs_since, context.source_change_delay
        )

    def evaluate_minimum_device_runtime(self, context: RuntimeContext) -> Permission:
        return self._evaluate_elapsed_time(context.now, context.device_started_at, context.minimum_device_runtime)

    def evaluate_minimum_source_runtime(self, context: RuntimeContext) -> Permission:
        return self._evaluate_elapsed_time(context.now, context.source_selected_at, context.minimum_source_runtime)

    def _evaluate_elapsed_time(
        self,
        now: float,
        reference_timestamp: float,
        required_delay: float,
    ) -> Permission:
        if now - reference_timestamp >= required_delay:
            return Permission.ALLOWED

        return Permission.DENIED
