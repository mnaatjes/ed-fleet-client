"""Pure-functional state reducer engine for materialized Elite Dangerous client projections."""

from __future__ import annotations

from .engine import TelemetryStateEngine, validate_mutex_invariants
from .models import (
    ClientStateProjection,
    LocationProjection,
    SessionProjection,
    ShipProjection,
)
from .reducers import (
    reduce_client_state,
    reduce_location,
    reduce_session,
    reduce_ship,
)

__all__ = (
    "ClientStateProjection",
    "LocationProjection",
    "SessionProjection",
    "ShipProjection",
    "TelemetryStateEngine",
    "reduce_client_state",
    "reduce_location",
    "reduce_session",
    "reduce_ship",
    "validate_mutex_invariants",
)
