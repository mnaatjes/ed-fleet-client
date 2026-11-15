"""High-level public SDK facade control plane for ed-fleet-client."""

from __future__ import annotations

from typing import Any

from ed_fleet_client.core.domain.dispatcher.dispatcher import TelemetryEventDispatcher
from ed_fleet_client.core.domain.services.orbital import OrbitalMechanicsService
from ed_fleet_client.core.domain.state.engine import TelemetryStateEngine
from ed_fleet_client.core.domain.state.models import ClientStateProjection
from ed_fleet_client.core.ports.driving.stream_port import StreamIngestionPort
from ed_fleet_client.core.use_cases.calculate_orbital_metrics import GetOrbitalMetricsUseCase
from ed_fleet_client.core.use_cases.dispatch_domain_events import ExecuteEventDispatchUseCase
from ed_fleet_client.core.use_cases.hydrate_snapshot_data import GetHydratedSnapshotUseCase
from ed_fleet_client.core.use_cases.stream_and_reduce_telemetry import (
    ProcessTelemetryStreamUseCase,
)


class EliteDangerousClient:
    """Unified public client facade coordinating telemetry streaming, state, and domain services."""

    def __init__(
        self,
        stream: StreamIngestionPort,
        stream_use_case: ProcessTelemetryStreamUseCase,
        dispatch_use_case: ExecuteEventDispatchUseCase,
        snapshot_use_case: GetHydratedSnapshotUseCase,
        orbital_use_case: GetOrbitalMetricsUseCase,
        state_engine: TelemetryStateEngine,
        dispatcher: TelemetryEventDispatcher,
        orbital_service: OrbitalMechanicsService,
    ) -> None:
        self._stream = stream
        self._stream_use_case = stream_use_case
        self._dispatch_use_case = dispatch_use_case
        self._snapshot_use_case = snapshot_use_case
        self._orbital_use_case = orbital_use_case
        self._state_engine = state_engine
        self._dispatcher = dispatcher
        self._orbital_service = orbital_service
        self._stream.on_event(self._handle_raw_event)

    def _handle_raw_event(self, raw: dict[str, Any]) -> None:
        self._stream_use_case.process_raw_event(raw)

    @property
    def state(self) -> ClientStateProjection:
        """Returns the current immutable materialized client state projection."""
        return self._state_engine.current

    @property
    def dispatcher(self) -> TelemetryEventDispatcher:
        """Returns the domain event dispatcher."""
        return self._dispatcher

    @property
    def orbital(self) -> GetOrbitalMetricsUseCase:
        """Returns the orbital metrics use case."""
        return self._orbital_use_case

    async def get_snapshot(self, name: str, endpoint: str) -> Any:
        """Fetches and hydrates a named companion snapshot via UC-03."""
        return await self._snapshot_use_case.execute(name, endpoint)

    async def connect(self) -> None:
        """Connects to the telemetry stream and begins state reduction."""
        await self._stream.start()

    async def disconnect(self) -> None:
        """Disconnects from the telemetry stream."""
        await self._stream.stop()
