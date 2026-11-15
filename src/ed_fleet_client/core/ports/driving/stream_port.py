"""Driving port contract for real-time telemetry stream ingestion."""

from __future__ import annotations

from typing import Any, Callable, Protocol, runtime_checkable  # noqa: UP035

from ed_fleet_client.core.ports.base import DrivingPort


@runtime_checkable
class StreamIngestionPort(DrivingPort, Protocol):
    """Primary port for starting, stopping, and subscribing to telemetry streams."""

    async def start(self) -> None:
        """Starts the telemetry stream ingestion loop."""
        ...

    async def stop(self) -> None:
        """Stops the telemetry stream ingestion loop."""
        ...

    def on_event(self, callback: Callable[[dict[str, Any]], None]) -> None:
        """Registers a callback invoked when a raw telemetry frame arrives."""
        ...
