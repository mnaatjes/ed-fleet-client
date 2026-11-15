"""Integration tests for EliteDangerousClient facade and container wiring."""

from __future__ import annotations

import pytest
from ed_models import JournalEvent

from ed_fleet_client import EliteDangerousClient, create_client
from ed_fleet_client.adapters.driven.telemetry_http import TelemetryConnectionConfig


def test_create_client_wires_facade() -> None:
    client = create_client(TelemetryConnectionConfig(host="127.0.0.1", port=8080))
    assert isinstance(client, EliteDangerousClient)
    assert client.state is not None
    assert client.location is not None
    assert client.session is not None
    assert client.ship is not None
    assert client.dispatcher is not None
    assert client.orbital is not None
    assert client.navigation is not None
    assert client.astrophysics is not None
    assert client.flight_performance is not None
    assert client.combat_analytics is not None


def test_facade_event_subscription_ergonomics() -> None:
    client = create_client(TelemetryConnectionConfig(host="127.0.0.1", port=8080))
    received: list[str] = []

    before = client.dispatcher.subscription_count

    @client.on(JournalEvent)
    def _on_event(event: JournalEvent) -> None:
        received.append(event.event)

    sub = client.subscribe(JournalEvent, _on_event)
    assert client.dispatcher.subscription_count == before + 2
    assert client.unsubscribe(sub) is True
    assert client.dispatcher.subscription_count == before + 1


@pytest.mark.asyncio
async def test_facade_async_context_manager() -> None:
    async with create_client(TelemetryConnectionConfig(host="127.0.0.1", port=8080)) as client:
        assert isinstance(client, EliteDangerousClient)
