"""Unit tests verifying initial state synchronization and historical frame filtering."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from typing import Any

import pytest

from ed_fleet_client import EliteDangerousClient, StreamMonitorConfig
from ed_fleet_client.adapters.driving.hydrator import TelemetryDomainHydrator
from ed_fleet_client.adapters.driving.stream.monitor import StreamMonitor
from ed_fleet_client.core.domain.dispatcher.dispatcher import TelemetryEventDispatcher
from ed_fleet_client.core.domain.services.astrophysics import AstrophysicsService
from ed_fleet_client.core.domain.services.combat_analytics import CombatAnalyticsService
from ed_fleet_client.core.domain.services.flight_performance import FlightPerformanceService
from ed_fleet_client.core.domain.services.navigation import NavigationService
from ed_fleet_client.core.domain.services.orbital import OrbitalMechanicsService
from ed_fleet_client.core.domain.state.engine import TelemetryStateEngine
from ed_fleet_client.core.ports.driven.telemetry_transport_port import TelemetryTransportPort
from ed_fleet_client.core.use_cases.calculate_orbital_metrics import GetOrbitalMetricsUseCase
from ed_fleet_client.core.use_cases.dispatch_domain_events import ExecuteEventDispatchUseCase
from ed_fleet_client.core.use_cases.hydrate_snapshot_data import GetHydratedSnapshotUseCase
from ed_fleet_client.core.use_cases.stream_and_reduce_telemetry import (
    ProcessTelemetryStreamUseCase,
)


class _MockTransport(TelemetryTransportPort):
    def __init__(self, frames: list[dict[str, Any]] | None = None) -> None:
        self.frames = frames or []

    async def fetch_status(self) -> dict[str, Any]:
        return {
            "Flags": 1,
            "Flags2": 0,
            "Pips": [4, 8, 0],
            "Fuel": {"FuelMain": 16.0, "FuelReservoir": 0.5},
            "Destination": {"System": 12345, "Name": "Chemaluk"},
        }

    async def fetch_state(self) -> dict[str, Any]:
        return {
            "state_sequence": 42,
            "game_status": {
                "exists": True,
                "Flags": 150994968,
                "Flags2": 0,
                "Pips": [4, 8, 0],
                "Destination": {"System": 2553114806643, "Name": "Chemaluk"},
            },
            "latest_journal_event": {
                "timestamp": "2026-11-16T03:20:00Z",
                "event": "FSDJump",
                "StarSystem": "Chemaluk",
            },
        }

    async def fetch_snapshot(self, endpoint: str) -> dict[str, Any]:
        return {}

    async def stream_events(self) -> AsyncIterator[dict[str, Any]]:
        for frame in self.frames:
            yield frame


@pytest.mark.asyncio
async def test_connect_seeds_initial_state_projection() -> None:
    transport = _MockTransport()
    hydrator = TelemetryDomainHydrator()
    stream = StreamMonitor(transport=transport)
    engine = TelemetryStateEngine()
    dispatcher = TelemetryEventDispatcher()
    state_accessor = lambda: engine.current  # noqa: E731

    orbital_svc = OrbitalMechanicsService(state_accessor=state_accessor, dispatcher=dispatcher)
    nav_svc = NavigationService(state_accessor=state_accessor, dispatcher=dispatcher)
    astro_svc = AstrophysicsService(state_accessor=state_accessor, dispatcher=dispatcher)
    flight_svc = FlightPerformanceService(state_accessor=state_accessor, dispatcher=dispatcher)
    combat_svc = CombatAnalyticsService(state_accessor=state_accessor, dispatcher=dispatcher)

    client = EliteDangerousClient(
        stream=stream,
        stream_use_case=ProcessTelemetryStreamUseCase(hydrator=hydrator, state_engine=engine),
        dispatch_use_case=ExecuteEventDispatchUseCase(dispatcher=dispatcher),
        snapshot_use_case=GetHydratedSnapshotUseCase(transport=transport, hydrator=hydrator),
        orbital_use_case=GetOrbitalMetricsUseCase(orbital_service=orbital_svc),
        state_engine=engine,
        dispatcher=dispatcher,
        orbital_service=orbital_svc,
        navigation_service=nav_svc,
        astrophysics_service=astro_svc,
        flight_performance_service=flight_svc,
        combat_analytics_service=combat_svc,
        transport=transport,
        hydrator=hydrator,
    )

    # Initial state should be default/empty
    assert client.location.star_system == "Unknown"

    # Connect with initial sync
    await client.connect(sync_initial_state=True)
    try:
        # State engine is now seeded from fetch_state()
        assert client.location.star_system == "Chemaluk"
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_stream_monitor_filters_historical_events() -> None:
    old_payload = '{"timestamp": "2026-11-16T01:00:00Z", "event": "FSDTarget", "Name": "Old"}'
    new_payload = '{"timestamp": "2026-11-16T05:00:00Z", "event": "FSDTarget", "Name": "New"}'

    historical_event = {
        "topic": "telemetry.journal",
        "timestamp": "2026-11-16T01:00:00Z",
        "payload": old_payload,
    }
    future_event = {
        "topic": "telemetry.journal",
        "timestamp": "2026-11-16T05:00:00Z",
        "payload": new_payload,
    }

    transport = _MockTransport(frames=[historical_event, future_event])
    config = StreamMonitorConfig(
        filter_historical=True,
        since_timestamp="2026-11-16T03:00:00Z",
    )
    monitor = StreamMonitor(transport=transport, config=config)

    received: list[dict[str, Any]] = []
    monitor.on_event(lambda f: received.append(f))

    await monitor.start()
    await asyncio.sleep(0.05)
    await monitor.stop()

    assert len(received) == 1
    assert "New" in received[0]["payload"]
