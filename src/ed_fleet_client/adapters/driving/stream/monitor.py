"""Driving stream monitor adapter implementing StreamIngestionPort."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import Any

from ed_fleet_client.core.ports.driven.telemetry_transport_port import TelemetryTransportPort

from .models import StreamMonitorConfig


class StreamMonitor:
    """Ingests telemetry frames from TelemetryTransportPort and notifies subscribers."""

    def __init__(
        self,
        transport: TelemetryTransportPort,
        config: StreamMonitorConfig | None = None,
    ) -> None:
        self._transport = transport
        self._config = config or StreamMonitorConfig()
        self._callbacks: list[Callable[[dict[str, Any]], None]] = []
        self._running = False
        self._task: asyncio.Task[None] | None = None

    @property
    def is_running(self) -> bool:
        """True if the stream monitor is actively ingesting events."""
        return self._running

    def on_event(self, callback: Callable[[dict[str, Any]], None]) -> None:
        """Registers a callback invoked when a raw telemetry frame arrives."""
        self._callbacks.append(callback)

    async def start(self) -> None:
        """Starts the telemetry stream ingestion loop."""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._run_loop())

    async def stop(self) -> None:
        """Stops the telemetry stream ingestion loop."""
        self._running = False
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def _run_loop(self) -> None:
        """Consumes events from the injected transport port with reconnect backoff."""
        while self._running:
            try:
                async for frame in self._transport.stream_events():
                    if not self._running:
                        break
                    for cb in self._callbacks:
                        cb(frame)
            except asyncio.CancelledError:
                raise
            except Exception:
                await asyncio.sleep(self._config.reconnect_delay_seconds)
                continue
            await asyncio.sleep(self._config.poll_interval_seconds)
