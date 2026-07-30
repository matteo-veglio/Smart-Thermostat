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

    def evaluate_minimum_runtime(self, context: RuntimeContext) -> Permission:
        # specs/12_controller_protection_workflow.md §3/§4: the single Minimum Runtime
        # protection, anchored to when the currently active device started operating.
        # Used both before stopping it and before replacing it with a different source.
        return self._evaluate_elapsed_time(context.now, context.device_started_at, context.minimum_runtime)

    def _evaluate_elapsed_time(
        self,
        now: float,
        reference_timestamp: float,
        required_delay: float,
    ) -> Permission:
        if now - reference_timestamp >= required_delay:
            return Permission.ALLOWED

        return Permission.DENIED
