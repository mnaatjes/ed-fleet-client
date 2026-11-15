"""Integration tests for EliteDangerousClient facade and container wiring."""

from __future__ import annotations

from ed_fleet_client import EliteDangerousClient, create_client
from ed_fleet_client.adapters.driven.telemetry_http import TelemetryConnectionConfig


def test_create_client_wires_facade() -> None:
    client = create_client(TelemetryConnectionConfig(host="127.0.0.1", port=8080))
    assert isinstance(client, EliteDangerousClient)
    assert client.state is not None
    assert client.dispatcher is not None
    assert client.orbital is not None
