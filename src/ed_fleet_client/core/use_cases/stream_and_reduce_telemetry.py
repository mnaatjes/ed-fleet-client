"""Use case for streaming and reducing telemetry events into client state (UC-01)."""

from __future__ import annotations

from typing import Any

from ed_fleet_client.core.domain.state.engine import TelemetryStateEngine
from ed_fleet_client.core.domain.state.models import ClientStateProjection
from ed_fleet_client.core.ports.driving.hydrator_port import HydratorPort


class ProcessTelemetryStreamUseCase:
    """Coordinates telemetry hydration and state reduction (UC-01)."""

    def __init__(self, hydrator: HydratorPort, state_engine: TelemetryStateEngine) -> None:
        self._hydrator = hydrator
        self._state_engine = state_engine

    def process_raw_event(self, raw: dict[str, Any]) -> tuple[ClientStateProjection, Any | None]:
        """Hydrates a raw telemetry payload, applies it to the state engine, and returns both."""
        # Support StatusTelemetry payloads (direct or wrapped in topic envelope)
        payload_str = raw.get("payload")
        raw_payload_str = raw.get("raw_payload")
        is_status = (
            "Flags" in raw
            or (isinstance(payload_str, str) and '"Flags"' in payload_str)
            or (isinstance(raw_payload_str, str) and '"Flags"' in raw_payload_str)
        )

        if is_status:
            status = self._hydrator.hydrate_status(raw)
            if status is not None:
                state = self._state_engine.apply(status)
                return state, status
            return self._state_engine.current, None

        event = self._hydrator.hydrate_journal_event(raw)
        if event is not None:
            state = self._state_engine.apply(event)
            return state, event
        return self._state_engine.current, None
