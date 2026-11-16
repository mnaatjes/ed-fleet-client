"""High-level public SDK facade control plane for ed-fleet-client."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

from ed_fleet_client.core.domain.dispatcher.dispatcher import TelemetryEventDispatcher
from ed_fleet_client.core.domain.dispatcher.models import (
    EventHandler,
    Subscription,
    TelemetryEvent,
)
from ed_fleet_client.core.domain.services.astrophysics import AstrophysicsService
from ed_fleet_client.core.domain.services.combat_analytics import CombatAnalyticsService
from ed_fleet_client.core.domain.services.flight_performance import FlightPerformanceService
from ed_fleet_client.core.domain.services.navigation import NavigationService
from ed_fleet_client.core.domain.services.orbital import OrbitalMechanicsService
from ed_fleet_client.core.domain.state.engine import TelemetryStateEngine
from ed_fleet_client.core.domain.state.models import (
    ClientStateProjection,
    LocationProjection,
    SessionProjection,
    ShipProjection,
)
from ed_fleet_client.core.ports.driving.stream_port import StreamIngestionPort
from ed_fleet_client.core.use_cases.calculate_orbital_metrics import GetOrbitalMetricsUseCase
from ed_fleet_client.core.use_cases.dispatch_domain_events import ExecuteEventDispatchUseCase
from ed_fleet_client.core.use_cases.hydrate_snapshot_data import GetHydratedSnapshotUseCase
from ed_fleet_client.core.use_cases.stream_and_reduce_telemetry import (
    ProcessTelemetryStreamUseCase,
)

E = TypeVar("E", bound=TelemetryEvent)


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
        navigation_service: NavigationService,
        astrophysics_service: AstrophysicsService,
        flight_performance_service: FlightPerformanceService,
        combat_analytics_service: CombatAnalyticsService,
    ) -> None:
        self._stream = stream
        self._stream_use_case = stream_use_case
        self._dispatch_use_case = dispatch_use_case
        self._snapshot_use_case = snapshot_use_case
        self._orbital_use_case = orbital_use_case
        self._state_engine = state_engine
        self._dispatcher = dispatcher
        self._orbital_service = orbital_service
        self._navigation_service = navigation_service
        self._astrophysics_service = astrophysics_service
        self._flight_performance_service = flight_performance_service
        self._combat_analytics_service = combat_analytics_service
        self._stream.on_event(self._handle_raw_event)

    def _handle_raw_event(self, raw: dict[str, Any]) -> None:
        _state, event = self._stream_use_case.process_raw_event(raw)
        if event is not None:
            self._dispatch_use_case.dispatch(event)

    async def __aenter__(self) -> EliteDangerousClient:
        """Connects to the telemetry stream when entering an async context."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Disconnects from the telemetry stream when exiting an async context."""
        await self.disconnect()

    def on(self, event_type: type[E]) -> Callable[[EventHandler], EventHandler]:
        """Decorator registering a handler callback for the specified domain event type."""
        return self._dispatcher.on(event_type)

    def subscribe(self, event_type: type[E], handler: EventHandler) -> Subscription:
        """Programmatically registers an event handler for a specific event type."""
        return self._dispatcher.subscribe(event_type, handler)

    def unsubscribe(self, subscription: Subscription) -> bool:
        """Removes an active event subscription."""
        return self._dispatcher.unsubscribe(subscription)

    @property
    def state(self) -> ClientStateProjection:
        """Returns the current immutable materialized client state projection."""
        return self._state_engine.current

    @property
    def location(self) -> LocationProjection:
        """Returns the current spatial location projection."""
        return self._state_engine.location

    @property
    def session(self) -> SessionProjection:
        """Returns the current commander/session projection."""
        return self._state_engine.session

    @property
    def ship(self) -> ShipProjection:
        """Returns the current ship hardware and status projection."""
        return self._state_engine.ship

    @property
    def dispatcher(self) -> TelemetryEventDispatcher:
        """Returns the domain event dispatcher."""
        return self._dispatcher

    @property
    def orbital(self) -> GetOrbitalMetricsUseCase:
        """Returns the orbital metrics use case."""
        return self._orbital_use_case

    @property
    def navigation(self) -> NavigationService:
        """Returns the navigation domain service."""
        return self._navigation_service

    @property
    def astrophysics(self) -> AstrophysicsService:
        """Returns the astrophysics domain service."""
        return self._astrophysics_service

    @property
    def flight_performance(self) -> FlightPerformanceService:
        """Returns the flight performance domain service."""
        return self._flight_performance_service

    @property
    def combat_analytics(self) -> CombatAnalyticsService:
        """Returns the combat analytics domain service."""
        return self._combat_analytics_service

    async def get_snapshot(self, name: str, endpoint: str) -> Any:
        """Fetches and hydrates a named companion snapshot via UC-03."""
        return await self._snapshot_use_case.execute(name, endpoint)

    async def connect(self) -> None:
        """Connects to the telemetry stream and begins state reduction."""
        await self._stream.start()

    async def disconnect(self) -> None:
        """Disconnects from the telemetry stream."""
        await self._stream.stop()
