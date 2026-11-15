"""Unit tests for NavigationService and geodetic algorithms."""

from __future__ import annotations

from ed_models import StatusTelemetry
from ed_models.core.domain.events import ApproachSettlement

from ed_fleet_client.core.domain.dispatcher import TelemetryEventDispatcher
from ed_fleet_client.core.domain.services.models import NavBearingUpdated
from ed_fleet_client.core.domain.services.navigation import (
    NavigationService,
    calculate_great_circle_bearing,
    calculate_surface_distance_km,
)
from ed_fleet_client.core.domain.state import ClientStateProjection, ShipProjection


def test_pure_geodesic_math() -> None:
    # Sol surface coordinates: Equator (0,0) to 45N, 0E -> Bearing should be 0.0 deg (due north)
    bearing = calculate_great_circle_bearing(0.0, 0.0, 45.0, 0.0)
    assert bearing == 0.0

    # Equator (0,0) to 0N, 45E -> Bearing should be 90.0 deg (due east)
    bearing_east = calculate_great_circle_bearing(0.0, 0.0, 0.0, 45.0)
    assert bearing_east == 90.0

    # Distance calculation on Earth radius (6371 km): 1 degree of latitude is ~111.19 km
    dist = calculate_surface_distance_km(0.0, 0.0, 1.0, 0.0, radius_km=6371.0)
    assert 111.0 <= dist <= 112.0


def test_navigation_service_pattern_1_state_guards() -> None:
    dispatcher = TelemetryEventDispatcher()
    current_state = ClientStateProjection()

    nav = NavigationService(
        state_accessor=lambda: current_state,
        dispatcher=dispatcher,
    )

    # Precondition Guard 1: No destination set -> returns None
    assert nav.bearing_to_target() is None
    assert nav.distance_to_target_km() is None

    # Precondition Guard 2: Destination set, but ship telemetry has no lat/lon -> returns None
    nav.set_destination("Dav's Hope", latitude=15.0, longitude=-25.0)
    assert nav.bearing_to_target() is None

    # Precondition Guard 3: Ship telemetry provided with coordinates
    telemetry = StatusTelemetry(latitude=10.0, longitude=-25.0, planet_radius=1000000.0)
    current_state = ClientStateProjection(ship=ShipProjection(telemetry=telemetry))

    # Now both conditions are satisfied -> returns valid numbers
    bearing = nav.bearing_to_target()
    assert bearing is not None
    assert bearing == 0.0  # (10N to 15N on same meridian is due north)

    dist = nav.distance_to_target_km()
    assert dist is not None
    assert dist > 0.0


def test_navigation_service_pattern_2_reactive_stream_pipe() -> None:
    dispatcher = TelemetryEventDispatcher()
    current_state = ClientStateProjection()

    nav = NavigationService(
        state_accessor=lambda: current_state,
        dispatcher=dispatcher,
    )
    assert nav.is_attached is True

    captured_events: list[NavBearingUpdated] = []

    @dispatcher.on(NavBearingUpdated)
    def handle_bearing_update(event: NavBearingUpdated) -> None:
        captured_events.append(event)

    # Trigger settlement event (updates target in nav service)
    settlement_ev = ApproachSettlement(
        timestamp="2026-11-09T05:30:00Z",
        event="ApproachSettlement",
        Name="Blackmount Orbital",
        Latitude=0.0,
        Longitude=50.0,
    )
    dispatcher.dispatch(settlement_ev)

    # No ship coordinates yet -> no NavBearingUpdated should have been fired
    assert len(captured_events) == 0

    # Supply ship coordinates and dispatch StatusTelemetry
    status = StatusTelemetry(latitude=0.0, longitude=40.0, heading=90.0)
    current_state = ClientStateProjection(ship=ShipProjection(telemetry=status))
    dispatcher.dispatch(status)

    # Both prerequisites now satisfied -> NavBearingUpdated fired reactively!
    assert len(captured_events) == 1
    ev = captured_events[0]
    assert ev.destination_name == "Blackmount Orbital"
    assert ev.bearing_deg == 90.0  # due east on equator
    assert ev.heading_deg == 90.0
    assert ev.deflection_deg == 0.0  # steering directly on course


def test_ship_targeting_and_route_progress() -> None:
    from ed_models.core.domain.events import FSDJump, FSDTarget, ShipTargeted

    from ed_fleet_client.core.domain.services.models import (
        RouteProgressUpdated,
        TargetLockedUpdated,
    )

    dispatcher = TelemetryEventDispatcher()
    current_state = ClientStateProjection()
    nav = NavigationService(
        state_accessor=lambda: current_state,
        dispatcher=dispatcher,
    )

    captured_targets: list[TargetLockedUpdated] = []
    captured_routes: list[RouteProgressUpdated] = []

    dispatcher.subscribe(TargetLockedUpdated, lambda e: captured_targets.append(e))
    dispatcher.subscribe(RouteProgressUpdated, lambda e: captured_routes.append(e))

    # 1. Target a vessel
    target_ev = ShipTargeted(
        timestamp="2026-11-09T05:35:00Z",
        event="ShipTargeted",
        TargetLocked=True,
        Ship="anaconda",
        Ship_Localised="Anaconda",
        PilotName="CMDR Jameson",
        ShieldHealth=0.85,
        HullHealth=1.0,
        LegalStatus="Clean",
    )
    dispatcher.dispatch(target_ev)

    assert len(captured_targets) == 1
    assert captured_targets[0].locked is True
    assert captured_targets[0].ship_model == "Anaconda"
    assert nav.locked_ship is not None
    assert nav.locked_ship["pilot_name"] == "CMDR Jameson"
    assert nav.locked_ship["shield_health"] == 0.85

    # 2. Plan hyperspace route
    fsd_target = FSDTarget(
        timestamp="2026-11-09T05:36:00Z",
        event="FSDTarget",
        Name="Sol",
        RemainingJumpsInRoute=3,
        StarClass="G",
    )
    dispatcher.dispatch(fsd_target)

    assert len(captured_routes) == 1
    assert captured_routes[0].destination_system == "Sol"
    assert captured_routes[0].remaining_jumps == 3
    assert nav.hyperspace_route is not None
    assert nav.hyperspace_route["remaining_jumps"] == 3

    # 3. Complete jump
    jump_ev = FSDJump(
        timestamp="2026-11-09T05:37:00Z",
        event="FSDJump",
        StarSystem="Alpha Centauri",
    )
    dispatcher.dispatch(jump_ev)
    assert nav.hyperspace_route is not None
    assert nav.hyperspace_route["remaining_jumps"] == 2
