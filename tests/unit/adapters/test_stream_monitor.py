"""Unit tests for StreamMonitor driving adapter."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from typing import Any

import pytest

from ed_fleet_client.adapters.driving.stream import StreamMonitor, StreamMonitorConfig
from ed_fleet_client.core.ports.driven.telemetry_transport_port import TelemetryTransportPort


class _FakeTransport(TelemetryTransportPort):
    async def fetch_status(self) -> dict[str, Any]:
        return {}

    async def fetch_snapshot(self, endpoint: str) -> dict[str, Any]:
        return {}

    async def stream_events(self) -> AsyncIterator[dict[str, Any]]:
        yield {"event": "FSDJump", "StarSystem": "Sol"}


@pytest.mark.asyncio
async def test_stream_monitor_emits_events_from_transport() -> None:
    monitor = StreamMonitor(
        transport=_FakeTransport(),
        config=StreamMonitorConfig(poll_interval_seconds=0.05),
    )
    received: list[dict[str, Any]] = []
    monitor.on_event(received.append)

    await monitor.start()
    await asyncio.sleep(0.05)
    await monitor.stop()

    assert monitor.is_running is False
    assert len(received) >= 1
    assert received[0]["StarSystem"] == "Sol"
