"""Use case for streaming and reducing telemetry events into client state (UC-01)."""

from __future__ import annotations

from typing import Any

from ..domain.state.engine import TelemetryStateEngine
from ..domain.state.models import ClientStateProjection
from ..ports.driving.hydrator_port import HydratorPort


class ProcessTelemetryStreamUseCase:
    """Coordinates telemetry hydration and state reduction (UC-01)."""

    def __init__(self, hydrator: HydratorPort, state_engine: TelemetryStateEngine) -> None:
        self._hydrator = hydrator
        self._state_engine = state_engine

    def process_raw_event(self, raw: dict[str, Any]) -> ClientStateProjection:
        """Hydrates a raw telemetry payload and applies it to the state engine."""
        if "Flags" in raw:
            status = self._hydrator.hydrate_status(raw)
            return self._state_engine.apply(status)
        event = self._hydrator.hydrate_journal_event(raw)
        return self._state_engine.apply(event)
