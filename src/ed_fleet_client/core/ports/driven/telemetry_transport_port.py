"""Driven port contract for outbound HTTP/SSE telemetry transport."""

from __future__ import annotations

from typing import Any, AsyncIterator, Protocol, runtime_checkable  # noqa: UP035

from ed_fleet_client.core.ports.base import DrivenPort


@runtime_checkable
class TelemetryTransportPort(DrivenPort, Protocol):
    """Secondary port implemented by outbound telemetry HTTP/SSE adapters."""

    async def fetch_status(self) -> dict[str, Any]:
        """Fetches the latest raw Status.json payload."""
        ...

    async def fetch_state(self) -> dict[str, Any]:
        """Fetches consolidated state payload from GET /api/v1/state."""
        ...

    async def fetch_snapshot(self, endpoint: str) -> dict[str, Any]:
        """Fetches a raw companion snapshot payload from the given endpoint."""
        ...

    def stream_events(self) -> AsyncIterator[dict[str, Any]]:
        """Streams raw telemetry event payloads."""
        ...
