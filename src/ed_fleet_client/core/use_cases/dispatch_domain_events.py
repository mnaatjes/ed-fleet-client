"""Use case for dispatching hydrated domain events to subscribers (UC-02)."""

from __future__ import annotations

from ..domain.dispatcher.dispatcher import TelemetryEventDispatcher
from ..domain.dispatcher.models import DispatchResult, TelemetryEvent


class ExecuteEventDispatchUseCase:
    """Orchestrates domain event dispatch through TelemetryEventDispatcher (UC-02)."""

    def __init__(self, dispatcher: TelemetryEventDispatcher) -> None:
        self._dispatcher = dispatcher

    def dispatch(self, event: TelemetryEvent) -> DispatchResult:
        """Synchronously dispatches a hydrated domain event."""
        return self._dispatcher.dispatch(event)

    async def dispatch_async(self, event: TelemetryEvent) -> DispatchResult:
        """Asynchronously dispatches a hydrated domain event."""
        return await self._dispatcher.dispatch_async(event)
