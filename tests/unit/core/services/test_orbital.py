"""Unit tests for OrbitalMechanicsService and Kepler propagation."""

from __future__ import annotations

import math
from datetime import datetime

from ed_models.core.domain.events import FSDJump
from ed_models.core.domain.events.exploration.scan import ScanPlanet
from ed_models.core.domain.spatial.coordinates import Coordinates3D

from ed_fleet_client.core.domain.dispatcher import TelemetryEventDispatcher
from ed_fleet_client.core.domain.services.models import BodyPositionPropagated
from ed_fleet_client.core.domain.services.orbital import (
    OrbitalMechanicsService,
    propagate_keplerian_orbit,
    solve_kepler_equation,
)
from ed_fleet_client.core.domain.state import ClientStateProjection


def test_solve_kepler_equation_circular_and_eccentric() -> None:
    # 1. Circular orbit (e = 0) -> E = M
    assert solve_kepler_equation(1.0, 0.0) == 1.0

    # 2. Eccentric orbit (e = 0.5, M = pi/2)
    m = math.pi / 2.0
    e_val = solve_kepler_equation(m, 0.5)
    # Check Kepler equation: E - e*sin(E) == M
    assert abs((e_val - 0.5 * math.sin(e_val)) - m) < 1e-7


def test_propagate_keplerian_orbit() -> None:
    # Earth-like circular orbit: ~150M km semi-major axis (~500 light-seconds)
    pos = propagate_keplerian_orbit(
        semi_major_axis_m=149_597_870_700.0,
        eccentricity=0.0,
        orbital_inclination_deg=0.0,
        periapsis_deg=0.0,
        ascending_node_deg=0.0,
        mean_anomaly_deg=0.0,
        orbital_period_s=31_557_600.0,
        epoch_timestamp_iso="2026-01-01T00:00:00Z",
        target_time=datetime.fromisoformat("2026-01-01T00:00:00+00:00"),
    )
    assert isinstance(pos, Coordinates3D)
    # At M=0, in-plane x should be approx 499 ls (1 AU / c)
    assert round(pos.x) == 499
    assert pos.y == 0.0
    assert pos.z == 0.0


def test_orbital_mechanics_service_reactive_ingest() -> None:
    dispatcher = TelemetryEventDispatcher()
    current_state = ClientStateProjection()
    orbital = OrbitalMechanicsService(
        state_accessor=lambda: current_state,
        dispatcher=dispatcher,
    )

    captured_events: list[BodyPositionPropagated] = []
    dispatcher.subscribe(BodyPositionPropagated, lambda e: captured_events.append(e))

    # Scan a planet
    scan = ScanPlanet(
        timestamp="2026-11-09T05:00:00Z",
        event="Scan",
        BodyName="Sol 3",
        BodyID=3,
        SemiMajorAxis=149_597_870_700.0,
        Eccentricity=0.0167,
        OrbitalInclination=0.0,
        Periapsis=102.9,
        AscendingNode=0.0,
        MeanAnomaly=358.6,
        OrbitalPeriod=31_557_600.0,
    )
    dispatcher.dispatch(scan)

    assert len(captured_events) == 1
    ev = captured_events[0]
    assert ev.body_name == "Sol 3"
    assert ev.body_id == 3
    assert ev.distance_from_barycenter_ls > 480.0

    # Test pull method
    bodies = orbital.list_bodies()
    assert len(bodies) == 1
    assert bodies[0]["body_name"] == "Sol 3"

    peri_apo = orbital.get_periapsis_apoapsis_ls(3)
    assert peri_apo is not None
    assert peri_apo[0] < peri_apo[1]

    # Test jump clears system bodies
    jump = FSDJump(timestamp="2026-11-09T06:00:00Z", event="FSDJump", StarSystem="Alpha Centauri")
    dispatcher.dispatch(jump)
    assert len(orbital.list_bodies()) == 0
