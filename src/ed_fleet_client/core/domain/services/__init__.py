"""Public API exports for ed-services package."""

from __future__ import annotations

from .astrophysics import (
    AstrophysicsService,
    calculate_habitable_zone_au,
    calculate_stellar_luminosity_solar,
)
from .base import TelemetryService
from .combat_analytics import (
    CombatAnalyticsService,
    calculate_sys_pip_resistance,
)
from .flight_performance import FlightPerformanceService
from .models import (
    BodyPositionPropagated,
    CombatDiagnosticsUpdated,
    HabitableZoneEvaluated,
    NavBearingUpdated,
    NavDistanceUpdated,
    OrbitalBodyRecord,
    PerformanceMetricsUpdated,
    RouteProgressUpdated,
    TargetLockedUpdated,
)
from .navigation import (
    NavigationService,
    calculate_great_circle_bearing,
    calculate_surface_distance_km,
)
from .orbital import (
    OrbitalMechanicsService,
    propagate_keplerian_orbit,
    solve_kepler_equation,
)

__all__ = (
    "AstrophysicsService",
    "BodyPositionPropagated",
    "CombatAnalyticsService",
    "CombatDiagnosticsUpdated",
    "FlightPerformanceService",
    "HabitableZoneEvaluated",
    "NavBearingUpdated",
    "NavDistanceUpdated",
    "NavigationService",
    "OrbitalBodyRecord",
    "OrbitalMechanicsService",
    "PerformanceMetricsUpdated",
    "RouteProgressUpdated",
    "TargetLockedUpdated",
    "TelemetryService",
    "calculate_great_circle_bearing",
    "calculate_habitable_zone_au",
    "calculate_stellar_luminosity_solar",
    "calculate_surface_distance_km",
    "calculate_sys_pip_resistance",
    "propagate_keplerian_orbit",
    "solve_kepler_equation",
)
