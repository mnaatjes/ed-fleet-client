"""In-memory test double for TelemetryTransportPort."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from ed_fleet_client.core.ports.driven.telemetry_transport_port import TelemetryTransportPort


class InMemoryTelemetryTransportPort(TelemetryTransportPort):
    """In-memory fake implementing TelemetryTransportPort for offline testing."""

    def __init__(
        self,
        status: dict[str, Any] | None = None,
        snapshots: dict[str, dict[str, Any]] | None = None,
        events: list[dict[str, Any]] | None = None,
    ) -> None:
        self._status = status or {}
        self._snapshots = snapshots or {}
        self._events = events or []

    async def fetch_status(self) -> dict[str, Any]:
        """Returns the configured in-memory status payload."""
        return dict(self._status)

    async def fetch_snapshot(self, endpoint: str) -> dict[str, Any]:
        """Returns the configured in-memory snapshot payload for the endpoint."""
        return dict(self._snapshots.get(endpoint, {}))

    async def stream_events(self) -> AsyncIterator[dict[str, Any]]:
        """Yields configured in-memory telemetry events."""
        for event in self._events:
            yield dict(event)
