"""Unit tests for analytical services: flight performance, combat, and astrophysics."""

from __future__ import annotations

from ed_models import StatusTelemetry
from ed_models.core.domain.events import Loadout, ShipTargeted
from ed_models.core.domain.events.exploration.scan import ScanPlanet, ScanStar

from ed_fleet_client.core.domain.dispatcher import TelemetryEventDispatcher
from ed_fleet_client.core.domain.services.astrophysics import (
    AstrophysicsService,
    calculate_habitable_zone_au,
    calculate_stellar_luminosity_solar,
)
from ed_fleet_client.core.domain.services.combat_analytics import (
    CombatAnalyticsService,
)
from ed_fleet_client.core.domain.services.flight_performance import FlightPerformanceService
from ed_fleet_client.core.domain.services.models import (
    CombatDiagnosticsUpdated,
    HabitableZoneEvaluated,
    PerformanceMetricsUpdated,
)
from ed_fleet_client.core.domain.state import ClientStateProjection, ShipProjection


def test_flight_performance_service() -> None:
    dispatcher = TelemetryEventDispatcher()
    status = StatusTelemetry(fuel_main=32.0, fuel_reservoir=0.5, cargo=64)
    state = ClientStateProjection(ship=ShipProjection(telemetry=status))

    service = FlightPerformanceService(state_accessor=lambda: state, dispatcher=dispatcher)

    events: list[PerformanceMetricsUpdated] = []
    dispatcher.subscribe(PerformanceMetricsUpdated, lambda e: events.append(e))

    # Loadout event: UnladenMass=400, MaxJumpRange=50.0 LY
    loadout = Loadout(
        timestamp="2026-11-10T01:00:00Z",
        event="Loadout",
        Ship="anaconda",
        UnladenMass=400.0,
        CargoCapacity=128,
        MaxJumpRange=50.0,
    )
    dispatcher.dispatch(loadout)

    assert len(events) == 1
    ev = events[0]
    # Total mass = 400 (unladen) + 64 (cargo) + 32.5 (fuel) = 496.5 t
    assert ev.total_mass_t == 496.5
    # Scaled jump range = 50.0 * (400 / 496.5) = 40.28 LY
    assert round(ev.max_jump_range_ly, 1) == 40.3
    assert service.get_total_mass_t() == 496.5


def test_combat_analytics_service() -> None:
    dispatcher = TelemetryEventDispatcher()
    status = StatusTelemetry(pips=(8, 4, 0))  # 4.0 SYS pips (8 half-pips)
    state = ClientStateProjection(ship=ShipProjection(telemetry=status))

    service = CombatAnalyticsService(state_accessor=lambda: state, dispatcher=dispatcher)

    events: list[CombatDiagnosticsUpdated] = []
    dispatcher.subscribe(CombatDiagnosticsUpdated, lambda e: events.append(e))

    # Test SYS pip hardening formula (4 pips = ~56.5% resistance)
    resistance = service.get_sys_pip_resistance()
    assert 0.56 <= resistance <= 0.57

    # Target vessel scan
    target_1 = ShipTargeted(
        timestamp="2026-11-10T01:05:00Z",
        event="ShipTargeted",
        TargetLocked=True,
        Ship="krait_mkii",
        ShieldHealth=1.0,
        HullHealth=1.0,
    )
    dispatcher.dispatch(target_1)
    assert len(events) == 1
    assert events[0].sys_pip_damage_resistance == resistance


def test_astrophysics_service() -> None:
    dispatcher = TelemetryEventDispatcher()
    state = ClientStateProjection()

    _service = AstrophysicsService(state_accessor=lambda: state, dispatcher=dispatcher)
    assert _service.is_in_habitable_zone(1.0) is True

    events: list[HabitableZoneEvaluated] = []
    dispatcher.subscribe(HabitableZoneEvaluated, lambda e: events.append(e))

    # Sun-like star: Radius=696,340,000 m, SurfaceTemperature=5778 K
    solar_lum = calculate_stellar_luminosity_solar(696_340_000.0, 5778.0)
    assert round(solar_lum, 2) == 1.0

    inner_au, outer_au = calculate_habitable_zone_au(1.0)
    assert 0.9 <= inner_au <= 1.0
    assert 1.3 <= outer_au <= 1.4

    # Scan Sun-like star
    star = ScanStar(
        timestamp="2026-11-10T01:10:00Z",
        event="Scan",
        BodyName="Sol",
        BodyID=0,
        Radius=696_340_000.0,
        SurfaceTemperature=5778.0,
    )
    dispatcher.dispatch(star)
    assert len(events) == 1
    assert events[0].star_name == "Sol"

    # Scan Earth-like planet at 1.0 AU (149,597,870,700 m)
    planet = ScanPlanet(
        timestamp="2026-11-10T01:11:00Z",
        event="Scan",
        BodyName="Sol 3",
        BodyID=3,
        SemiMajorAxis=149_597_870_700.0,
    )
    dispatcher.dispatch(planet)
    assert len(events) == 2
    assert events[1].planet_name == "Sol 3"
    assert events[1].in_habitable_zone is True
