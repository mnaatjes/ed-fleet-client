"""Pure-functional event reducers projecting ed-models events into immutable state projections."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime
from typing import Any

from ed_models import JournalEvent, StatusTelemetry

from .models import (
    ClientStateProjection,
    LocationProjection,
    SessionProjection,
    ShipProjection,
)


def _safe_tuple3(val: Any) -> tuple[float, float, float]:
    if isinstance(val, list | tuple) and len(val) >= 3:
        try:
            return (float(val[0]), float(val[1]), float(val[2]))
        except (ValueError, TypeError):
            pass
    return (0.0, 0.0, 0.0)


def reduce_location(current: LocationProjection, event: JournalEvent) -> LocationProjection:
    """Projects spatial location events (FSDJump, Location, CarrierJump, Docked, Undocked, etc.)."""
    ev_name = getattr(event, "event", "")
    now = datetime.now(UTC)

    if ev_name in ("FSDJump", "Location", "CarrierJump"):
        star_system = getattr(event, "StarSystem", current.star_system)
        system_address = getattr(event, "SystemAddress", current.system_address)
        star_pos = _safe_tuple3(getattr(event, "StarPos", current.star_pos))
        body = getattr(event, "Body", current.body)
        body_id = getattr(event, "BodyID", current.body_id)
        body_type = getattr(event, "BodyType", current.body_type)
        docked = bool(getattr(event, "Docked", False))
        station_name = getattr(event, "StationName", None if not docked else current.station_name)
        station_type = getattr(event, "StationType", None if not docked else current.station_type)
        market_id = getattr(event, "MarketID", current.market_id)
        population = int(getattr(event, "Population", current.population) or 0)
        allegiance = str(getattr(event, "SystemAllegiance", current.allegiance) or "")
        economy = str(
            getattr(
                event,
                "SystemEconomy_Localised",
                getattr(event, "SystemEconomy", current.economy),
            )
            or ""
        )
        government = str(
            getattr(
                event,
                "SystemGovernment_Localised",
                getattr(event, "SystemGovernment", current.government),
            )
            or ""
        )
        security = str(
            getattr(
                event,
                "SystemSecurity_Localised",
                getattr(event, "SystemSecurity", current.security),
            )
            or ""
        )

        return replace(
            current,
            star_system=star_system,
            system_address=system_address,
            star_pos=star_pos,
            body=body,
            body_id=body_id,
            body_type=body_type,
            station_name=station_name,
            station_type=station_type,
            market_id=market_id,
            docked=docked,
            in_supercruise=not docked,
            population=population,
            allegiance=allegiance,
            economy=economy,
            government=government,
            security=security,
            last_updated=now,
        )

    if ev_name in ("Docked",):
        station_name = getattr(event, "StationName", current.station_name)
        station_type = getattr(event, "StationType", current.station_type)
        market_id = getattr(event, "MarketID", current.market_id)
        return replace(
            current,
            docked=True,
            in_supercruise=False,
            station_name=station_name,
            station_type=station_type,
            market_id=market_id,
            last_updated=now,
        )

    if ev_name in ("Undocked",):
        return replace(
            current,
            docked=False,
            station_name=None,
            station_type=None,
            last_updated=now,
        )

    if ev_name in ("SupercruiseEntry",):
        return replace(current, in_supercruise=True, last_updated=now)

    if ev_name in ("SupercruiseExit",):
        body = getattr(event, "Body", current.body)
        body_type = getattr(event, "BodyType", current.body_type)
        body_id = getattr(event, "BodyID", current.body_id)
        return replace(
            current,
            in_supercruise=False,
            body=body,
            body_type=body_type,
            body_id=body_id,
            last_updated=now,
        )

    if ev_name in ("ApproachBody",):
        body = getattr(event, "Body", current.body)
        body_id = getattr(event, "BodyID", current.body_id)
        return replace(current, body=body, body_id=body_id, last_updated=now)

    return current


def reduce_session(current: SessionProjection, event: JournalEvent) -> SessionProjection:
    """Projects session and commander lifecycle events."""
    ev_name = getattr(event, "event", "")
    now = datetime.now(UTC)

    if ev_name == "Commander":
        cmd_name = getattr(event, "Name", current.commander_name)
        fid = getattr(event, "FID", current.fid)
        return replace(current, commander_name=cmd_name, fid=fid, last_updated=now)

    if ev_name == "LoadGame":
        cmd_name = getattr(event, "Commander", current.commander_name)
        fid = getattr(event, "FID", current.fid)
        mode = getattr(event, "GameMode", current.game_mode)
        group = getattr(event, "Group", current.group)
        credits_val = int(getattr(event, "Credits", current.credits) or 0)
        loan_val = int(getattr(event, "Loan", current.loan) or 0)
        is_odyssey = bool(getattr(event, "Odyssey", current.is_odyssey))
        return replace(
            current,
            commander_name=cmd_name,
            fid=fid,
            game_mode=mode,
            group=group,
            credits=credits_val,
            loan=loan_val,
            is_odyssey=is_odyssey,
            is_alive=True,
            last_updated=now,
        )

    if ev_name == "Fileheader":
        odyssey = bool(getattr(event, "Odyssey", current.is_odyssey))
        version = str(getattr(event, "gameversion", current.game_version) or "")
        return replace(current, is_odyssey=odyssey, game_version=version, last_updated=now)

    if ev_name == "Died":
        return replace(current, is_alive=False, last_updated=now)

    if ev_name == "Resurrect":
        return replace(current, is_alive=True, last_updated=now)

    return current


def reduce_ship(
    current: ShipProjection,
    event: JournalEvent | StatusTelemetry,
) -> ShipProjection:
    """Projects ship loadout, cockpit telemetry, and hardware attributes."""
    now = datetime.now(UTC)

    if isinstance(event, StatusTelemetry):
        return replace(current, telemetry=event, last_updated=now)

    ev_name = getattr(event, "event", "")

    if ev_name == "Loadout":
        ship_type = getattr(event, "Ship", current.ship_type)
        ship_name = getattr(event, "ShipName", current.ship_name)
        ship_ident = getattr(event, "ShipIdent", current.ship_ident)
        hull_val = int(getattr(event, "HullValue", current.hull_value) or 0)
        mods_val = int(getattr(event, "ModulesValue", current.modules_value) or 0)
        rebuy = int(getattr(event, "Rebuy", current.rebuy) or 0)
        unladen_mass = float(getattr(event, "UnladenMass", current.unladen_mass) or 0.0)
        cargo_cap = int(getattr(event, "CargoCapacity", current.cargo_capacity) or 0)
        max_jump = float(getattr(event, "MaxJumpRange", current.max_jump_range) or 0.0)

        return replace(
            current,
            ship_type=ship_type,
            ship_name=ship_name,
            ship_ident=ship_ident,
            hull_value=hull_val,
            modules_value=mods_val,
            rebuy=rebuy,
            unladen_mass=unladen_mass,
            cargo_capacity=cargo_cap,
            max_jump_range=max_jump,
            last_updated=now,
        )

    if ev_name == "ShipyardBuy":
        ship_type = getattr(event, "ShipType", current.ship_type)
        return replace(current, ship_type=ship_type, last_updated=now)

    if ev_name == "ShipyardSwap":
        ship_type = getattr(event, "ShipType", current.ship_type)
        return replace(current, ship_type=ship_type, last_updated=now)

    return current


def reduce_client_state(
    current: ClientStateProjection,
    event: JournalEvent | StatusTelemetry,
) -> ClientStateProjection:
    """Root pure reducer folding incoming event into the root ClientStateProjection."""
    now_seq = current.sequence_number + 1

    if isinstance(event, StatusTelemetry):
        new_ship = reduce_ship(current.ship, event)
        return replace(
            current,
            ship=new_ship,
            sequence_number=now_seq,
            last_event_name="StatusTelemetry",
            last_event_timestamp=datetime.now(UTC).isoformat(),
        )

    ev_name = getattr(event, "event", "UnknownEvent")
    ev_timestamp = getattr(event, "timestamp", "")

    new_loc = reduce_location(current.location, event)
    new_sess = reduce_session(current.session, event)
    new_ship = reduce_ship(current.ship, event)

    return replace(
        current,
        location=new_loc,
        session=new_sess,
        ship=new_ship,
        sequence_number=now_seq,
        last_event_name=ev_name,
        last_event_timestamp=ev_timestamp,
    )
