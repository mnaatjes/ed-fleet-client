"""Offline unit tests for UC-01 through UC-04 use cases."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

import pytest
from ed_models import JournalEvent

from ed_fleet_client.adapters.driving.hydrator import TelemetryDomainHydrator
from ed_fleet_client.core.domain.dispatcher.dispatcher import TelemetryEventDispatcher
from ed_fleet_client.core.domain.services.orbital import OrbitalMechanicsService
from ed_fleet_client.core.domain.state.engine import TelemetryStateEngine
from ed_fleet_client.core.ports.driven.telemetry_transport_port import TelemetryTransportPort
from ed_fleet_client.core.use_cases.calculate_orbital_metrics import GetOrbitalMetricsUseCase
from ed_fleet_client.core.use_cases.dispatch_domain_events import ExecuteEventDispatchUseCase
from ed_fleet_client.core.use_cases.hydrate_snapshot_data import GetHydratedSnapshotUseCase
from ed_fleet_client.core.use_cases.stream_and_reduce_telemetry import (
    ProcessTelemetryStreamUseCase,
)


class _FakeTransport(TelemetryTransportPort):
    async def fetch_status(self) -> dict[str, Any]:
        return {"Flags": 1}

    async def fetch_snapshot(self, endpoint: str) -> dict[str, Any]:
        return {"MarketID": 128114, "StationName": "Jameson Memorial"}

    async def stream_events(self) -> AsyncIterator[dict[str, Any]]:
        yield {"event": "FSDJump", "StarSystem": "Sol"}


def test_uc01_process_telemetry_stream() -> None:
    hydrator = TelemetryDomainHydrator()
    engine = TelemetryStateEngine()
    uc = ProcessTelemetryStreamUseCase(hydrator=hydrator, state_engine=engine)

    state, event = uc.process_raw_event(
        {
            "timestamp": "2026-11-15T00:00:00Z",
            "event": "FSDJump",
            "StarSystem": "Shinrarta Dezhra",
        }
    )
    assert state.location.star_system == "Shinrarta Dezhra"
    assert event is not None
    assert event.event == "FSDJump"


def test_uc02_execute_event_dispatch() -> None:
    dispatcher = TelemetryEventDispatcher()
    received: list[str] = []

    @dispatcher.on(JournalEvent)
    def _on_jump(event: JournalEvent) -> None:
        received.append(event.event)

    uc = ExecuteEventDispatchUseCase(dispatcher=dispatcher)
    result = uc.dispatch(JournalEvent(timestamp="2026-11-15T00:00:00Z", event="FSDJump"))
    assert result.executed_count == 1
    assert received == ["FSDJump"]


@pytest.mark.asyncio
async def test_uc03_get_hydrated_snapshot() -> None:
    uc = GetHydratedSnapshotUseCase(
        transport=_FakeTransport(),
        hydrator=TelemetryDomainHydrator(),
    )
    snap = await uc.execute("Market", "/api/v1/snapshots/market")
    assert snap.target_name == "Market"
    assert snap.data["MarketID"] == 128114


def test_uc04_get_orbital_metrics() -> None:
    engine = TelemetryStateEngine()
    dispatcher = TelemetryEventDispatcher()
    service = OrbitalMechanicsService(
        state_accessor=lambda: engine.current,
        dispatcher=dispatcher,
    )
    uc = GetOrbitalMetricsUseCase(orbital_service=service)
    assert uc.list_tracked_bodies() == []
