"""Use case for fetching and hydrating companion snapshot data (UC-03)."""

from __future__ import annotations

from typing import Any

from ed_fleet_client.core.ports.driven.telemetry_transport_port import TelemetryTransportPort
from ed_fleet_client.core.ports.driving.hydrator_port import HydratorPort


class GetHydratedSnapshotUseCase:
    """Fetches raw snapshot payloads via transport port and hydrates them (UC-03)."""

    def __init__(self, transport: TelemetryTransportPort, hydrator: HydratorPort) -> None:
        self._transport = transport
        self._hydrator = hydrator

    async def execute(self, snapshot_name: str, endpoint: str) -> Any:
        """Fetches a snapshot from the transport port and returns the hydrated model."""
        raw = await self._transport.fetch_snapshot(endpoint)
        return self._hydrator.hydrate_snapshot(snapshot_name, raw)
