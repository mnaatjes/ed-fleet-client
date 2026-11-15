"""Composition root wiring concrete adapters to core ports and use cases."""

from __future__ import annotations

from ..adapters.driven.telemetry_http.client import TelemetryHttpClient
from ..adapters.driven.telemetry_http.models import TelemetryConnectionConfig
from ..adapters.driving.hydrator.hydrator import TelemetryDomainHydrator
from ..adapters.driving.stream.monitor import StreamMonitor
from ..client import EliteDangerousClient
from ..core.domain.dispatcher.dispatcher import TelemetryEventDispatcher
from ..core.domain.services.orbital import OrbitalMechanicsService
from ..core.domain.state.engine import TelemetryStateEngine
from ..core.use_cases.calculate_orbital_metrics import GetOrbitalMetricsUseCase
from ..core.use_cases.dispatch_domain_events import ExecuteEventDispatchUseCase
from ..core.use_cases.stream_and_reduce_telemetry import ProcessTelemetryStreamUseCase


def create_client(config: TelemetryConnectionConfig | None = None) -> EliteDangerousClient:
    """Builds and wires a complete EliteDangerousClient instance."""
    transport = TelemetryHttpClient(config=config)
    hydrator = TelemetryDomainHydrator()
    stream = StreamMonitor(transport=transport)

    state_engine = TelemetryStateEngine()
    dispatcher = TelemetryEventDispatcher()
    orbital_service = OrbitalMechanicsService(
        state_accessor=lambda: state_engine.current,
        dispatcher=dispatcher,
    )

    stream_use_case = ProcessTelemetryStreamUseCase(
        hydrator=hydrator,
        state_engine=state_engine,
    )
    dispatch_use_case = ExecuteEventDispatchUseCase(dispatcher=dispatcher)
    orbital_use_case = GetOrbitalMetricsUseCase(orbital_service=orbital_service)

    return EliteDangerousClient(
        stream=stream,
        stream_use_case=stream_use_case,
        dispatch_use_case=dispatch_use_case,
        orbital_use_case=orbital_use_case,
        state_engine=state_engine,
        dispatcher=dispatcher,
        orbital_service=orbital_service,
    )
