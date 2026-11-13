"""Unit tests for ed_reducer pure reducer functions."""

from __future__ import annotations

from ed_models import StatusTelemetry
from ed_models.core.domain.events import (
    ApproachBody,
    Docked,
    FSDJump,
    LoadGame,
    Loadout,
    Location,
    Undocked,
)

from ed_fleet_client.core.domain.state.models import (
    ClientStateProjection,
    LocationProjection,
    SessionProjection,
    ShipProjection,
)
from ed_fleet_client.core.domain.state.reducers import (
    reduce_client_state,
    reduce_location,
    reduce_session,
    reduce_ship,
)


def test_reduce_location_fsd_jump() -> None:
    initial = LocationProjection()
    jump_event = FSDJump(
        timestamp="2026-11-09T03:30:00Z",
        event="FSDJump",
        StarSystem="Sol",
        SystemAddress=10477373803,
        StarPos=(0.0, 0.0, 0.0),
        Body="Sol",
        BodyID=0,
        BodyType="Star",
        Population=22800000000,
        SystemAllegiance="Federation",
        SystemEconomy="Refinery",
        SystemGovernment="Democracy",
        SystemSecurity="High",
    )

    updated = reduce_location(initial, jump_event)

    assert updated.star_system == "Sol"
    assert updated.system_address == 10477373803
    assert updated.star_pos == (0.0, 0.0, 0.0)
    assert updated.body == "Sol"
    assert updated.population == 22800000000
    assert updated.allegiance == "Federation"
    assert updated.in_supercruise is True
    assert updated.docked is False


def test_reduce_location_docked_undocked() -> None:
    loc = LocationProjection(star_system="Sol", in_supercruise=True, docked=False)

    docked_ev = Docked(
        timestamp="2026-11-09T03:35:00Z",
        event="Docked",
        StationName="Mars High",
        StationType="Orbis",
        MarketID=1280001,
    )

    docked_loc = reduce_location(loc, docked_ev)
    assert docked_loc.docked is True
    assert docked_loc.in_supercruise is False
    assert docked_loc.station_name == "Mars High"
    assert docked_loc.station_type == "Orbis"

    undocked_ev = Undocked(
        timestamp="2026-11-09T03:40:00Z",
        event="Undocked",
    )
    undocked_loc = reduce_location(docked_loc, undocked_ev)
    assert undocked_loc.docked is False
    assert undocked_loc.station_name is None


def test_reduce_session_load_game() -> None:
    initial = SessionProjection()
    load_ev = LoadGame(
        timestamp="2026-11-09T03:00:00Z",
        event="LoadGame",
        Commander="Jameson",
        FID="F123456",
        GameMode="Open",
        Group="",
        Credits=500000000,
        Loan=0,
        Odyssey=True,
    )

    updated = reduce_session(initial, load_ev)
    assert updated.commander_name == "Jameson"
    assert updated.fid == "F123456"
    assert updated.game_mode == "Open"
    assert updated.credits == 500000000
    assert updated.is_odyssey is True
    assert updated.is_alive is True


def test_reduce_ship_loadout_and_status() -> None:
    initial = ShipProjection()
    loadout_ev = Loadout(
        timestamp="2026-11-09T03:10:00Z",
        event="Loadout",
        Ship="anaconda",
        ShipName="Voyager",
        ShipIdent="NX-01",
        HullValue=140000000,
        ModulesValue=200000000,
        Rebuy=17000000,
        CargoCapacity=320,
    )

    ship = reduce_ship(initial, loadout_ev)
    assert ship.ship_type == "anaconda"
    assert ship.ship_name == "Voyager"
    assert ship.ship_ident == "NX-01"
    assert ship.cargo_capacity == 320

    status = StatusTelemetry(cargo=42)
    ship_with_status = reduce_ship(ship, status)
    assert ship_with_status.telemetry is not None
    assert ship_with_status.telemetry.cargo == 42
    assert ship_with_status.ship_name == "Voyager"


def test_reduce_client_state_transient_passthrough() -> None:
    initial = ClientStateProjection()
    loc_ev = Location(
        timestamp="2026-11-09T03:00:00Z",
        event="Location",
        StarSystem="Shinrarta Dezhra",
    )
    s1 = reduce_client_state(initial, loc_ev)
    assert s1.location.star_system == "Shinrarta Dezhra"
    assert s1.sequence_number == 1
    assert s1.last_event_name == "Location"

    # Transient event (e.g. ApproachBody) updates body but keeps system
    approach = ApproachBody(
        timestamp="2026-11-09T03:05:00Z",
        event="ApproachBody",
        Body="Founders World",
        BodyID=1,
    )
    s2 = reduce_client_state(s1, approach)
    assert s2.location.star_system == "Shinrarta Dezhra"
    assert s2.location.body == "Founders World"
    assert s2.sequence_number == 2
