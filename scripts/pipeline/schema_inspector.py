"""AST Schema reflection and property classification for ed-models."""

import dataclasses
import inspect
from dataclasses import dataclass, fields, is_dataclass
from typing import get_type_hints

import ed_models.core.domain.events as ev
from ed_models.core.domain.status.telemetry import StatusTelemetry


@dataclass(frozen=True)
class EventFieldMeta:
    """Metadata describing a field extracted from an event or telemetry model."""

    field_name: str
    canonical_property: str
    field_type: str
    is_optional: bool
    is_authoritative_id: bool


@dataclass(frozen=True)
class EventSchemaMeta:
    """Metadata describing an event schema and its extracted fields."""

    event_name: str
    module_path: str
    is_status: bool
    fields: dict[str, EventFieldMeta]


CANONICAL_PROPERTY_MAP: dict[str, str] = {
    # System & Navigation
    "star_system": "star_system",
    "starsystem": "star_system",
    "system_name": "star_system",
    "systemaddress": "system_address",
    "system_address": "system_address",
    "starpos": "coordinates",
    "coordinates": "coordinates",
    "system_allegiance": "allegiance",
    "systemallegiance": "allegiance",
    "system_economy": "economy",
    "systemeconomy": "economy",
    "system_government": "government",
    "systemgovernment": "government",
    "system_security": "security",
    "systemsecurity": "security",
    "population": "population",
    # Body / Planet
    "body": "body_name",
    "body_name": "body_name",
    "bodyid": "body_id",
    "body_id": "body_id",
    "bodytype": "body_type",
    "body_type": "body_type",
    # Station & Market
    "station_name": "station_name",
    "stationname": "station_name",
    "station_type": "station_type",
    "stationtype": "station_type",
    "market_id": "market_id",
    "marketid": "market_id",
    "station_allegiance": "station_allegiance",
    "stationallegiance": "station_allegiance",
    "station_economy": "station_economy",
    "stationeconomy": "station_economy",
    "station_government": "station_government",
    "stationgovernment": "station_government",
    # Vessel & Loadout
    "ship": "ship_model",
    "ship_type": "ship_model",
    "shiptype": "ship_model",
    "ship_id": "ship_id",
    "shipid": "ship_id",
    "ship_name": "ship_name",
    "shipname": "ship_name",
    "ship_ident": "ship_ident",
    "shipident": "ship_ident",
    "fuel_main": "fuel_main",
    "fuel_reservoir": "fuel_reservoir",
    "hull_value": "hull_value",
    "hull_health": "hull_health",
    "hullhealth": "hull_health",
    "unladen_mass": "unladen_mass",
    "cargo_capacity": "cargo_capacity",
    "max_jump_range": "max_jump_range",
    # Commander & Session
    "commander": "cmdr_name",
    "commander_name": "cmdr_name",
    "fid": "cmdr_fid",
    "credits": "credits",
    "loan": "loan",
    "game_mode": "game_mode",
    # Operational Telemetry (Status.json)
    "flags": "flags",
    "flags2": "flags2",
    "pips": "pips",
    "firegroup": "firegroup",
    "gui_focus": "gui_focus",
    "fuel": "fuel",
    "cargo": "cargo",
    "legal_state": "legal_state",
    "latitude": "latitude",
    "longitude": "longitude",
    "altitude": "altitude",
    "heading": "heading",
    "planet_radius": "planet_radius",
    "oxygen": "oxygen",
    "health": "health",
    "temperature": "temperature",
    "gravity": "gravity",
}

PROPERTY_TIERS: dict[str, int] = {
    # Tier 1: Core Navigation & Session Identity
    "star_system": 1,
    "system_address": 1,
    "coordinates": 1,
    "body_name": 1,
    "body_id": 1,
    "ship_model": 1,
    "ship_id": 1,
    "ship_name": 1,
    "ship_ident": 1,
    "cmdr_name": 1,
    "cmdr_fid": 1,
    "docked": 1,
    # Tier 2: Operational Vessel & Flight Telemetry
    "fuel_main": 2,
    "fuel_reservoir": 2,
    "fuel": 2,
    "pips": 2,
    "hull_health": 2,
    "flags": 2,
    "flags2": 2,
    "firegroup": 2,
    "gui_focus": 2,
    "heading": 2,
    "altitude": 2,
    "latitude": 2,
    "longitude": 2,
    "max_jump_range": 2,
    "cargo_capacity": 2,
    # Tier 3: Contextual, Market & Station State
    "station_name": 3,
    "station_type": 3,
    "market_id": 3,
    "credits": 3,
    "loan": 3,
    "economy": 3,
    "government": 3,
    "allegiance": 3,
    "security": 3,
    "population": 3,
    # Default Tier 4: Ephemeral & Granular Details
}


class SchemaInspector:
    """Reflects schema definitions across ed-models to map properties to event models."""

    def __init__(self) -> None:
        self.events_metadata: dict[str, EventSchemaMeta] = {}
        self.property_to_events: dict[str, list[str]] = {}

    def normalize_property_name(self, raw_field: str) -> str:
        """Map raw field name to canonical property name."""
        lowered = raw_field.lower()
        return CANONICAL_PROPERTY_MAP.get(lowered, lowered)

    def get_property_tier(self, canonical_property: str) -> int:
        """Return the importance tier (1-4) for a property."""
        return PROPERTY_TIERS.get(canonical_property, 4)

    def inspect_class(self, cls: type, is_status: bool = False) -> EventSchemaMeta | None:
        """Inspect a single dataclass/event model."""
        if not is_dataclass(cls):
            return None

        cls_fields: dict[str, EventFieldMeta] = {}
        try:
            type_hints = get_type_hints(cls)
        except Exception:
            type_hints = {}

        for f in fields(cls):
            raw_name = f.name
            canon = self.normalize_property_name(raw_name)
            type_str = str(type_hints.get(raw_name, f.type))
            is_opt = "Optional" in type_str or "None" in type_str
            is_auth = (
                canon in ("system_address", "market_id", "body_id", "ship_id", "cmdr_fid")
                or "address" in canon
                or "id" in canon
            )

            meta = EventFieldMeta(
                field_name=raw_name,
                canonical_property=canon,
                field_type=type_str,
                is_optional=is_opt,
                is_authoritative_id=is_auth,
            )
            cls_fields[raw_name] = meta

        event_name = cls.__name__
        module_path = cls.__module__

        return EventSchemaMeta(
            event_name=event_name,
            module_path=module_path,
            is_status=is_status,
            fields=cls_fields,
        )

    def discover_all_schemas(self) -> dict[str, EventSchemaMeta]:
        """Discover and inspect all journal events and StatusTelemetry in ed-models."""
        results: dict[str, EventSchemaMeta] = {}

        # 1. StatusTelemetry
        status_meta = self.inspect_class(StatusTelemetry, is_status=True)
        if status_meta:
            results["StatusTelemetry"] = status_meta

        # 2. Inspect all classes exported in ed_models.core.domain.events
        for name in dir(ev):
            if name.startswith("_"):
                continue
            obj = getattr(ev, name)
            if inspect.isclass(obj) and is_dataclass(obj):
                meta = self.inspect_class(obj, is_status=False)
                if meta:
                    results[meta.event_name] = meta

        self.events_metadata = results

        # Build reverse index: property -> list of event names
        rev_index: dict[str, list[str]] = {}
        for ev_name, ev_meta in results.items():
            for f_meta in ev_meta.fields.values():
                canon = f_meta.canonical_property
                if canon not in rev_index:
                    rev_index[canon] = []
                if ev_name not in rev_index[canon]:
                    rev_index[canon].append(ev_name)

        self.property_to_events = rev_index
        return results


def discover_projection_targets() -> dict[str, str]:
    """Dynamically introspects ClientStateProjection dataclasses and StatusTelemetry
    to discover all valid dot-notation projection paths, mapping canonical property
    names to their state projection targets.
    """
    from typing import get_type_hints

    import ed_fleet_client.core.domain.state.models as state_models
    from ed_fleet_client.core.domain.state.models import ClientStateProjection

    targets: dict[str, str] = {}
    client_hints = get_type_hints(ClientStateProjection, vars(state_models))

    # 1. Reflect child dataclasses on ClientStateProjection (location, session, ship)
    for child_name, child_cls in client_hints.items():
        if isinstance(child_cls, type) and is_dataclass(child_cls):
            child_hints = get_type_hints(child_cls, vars(state_models))
            for prop_name in child_hints:
                if prop_name in ("last_updated", "__post_init__"):
                    continue
                targets[prop_name] = f"{child_name}.{prop_name}"

    # 2. Reflect StatusTelemetry nested under ship.telemetry
    status_hints = get_type_hints(StatusTelemetry)
    for st_name in status_hints:
        if st_name != "additional_fields":
            targets[st_name] = f"ship.telemetry.{st_name}"
            targets[st_name.lower()] = f"ship.telemetry.{st_name}"

    # 3. Canonical aliases bridge (mapping normalized event properties to projection fields)
    aliases: dict[str, str] = {
        "coordinates": "location.star_pos",
        "body_name": "location.body",
        "ship_model": "ship.ship_type",
        "cmdr_name": "session.commander_name",
        "cmdr_fid": "session.fid",
        "fuel_main": "ship.telemetry.fuel_main",
        "fuel_reservoir": "ship.telemetry.fuel_reservoir",
        "fuel": "ship.telemetry.fuel_main",
        "hull_health": "ship.hull_health",
        "pips": "ship.telemetry.pips",
        "flags": "ship.telemetry.flags",
        "flags2": "ship.telemetry.flags2",
        "heading": "ship.telemetry.heading",
        "altitude": "ship.telemetry.altitude",
        "latitude": "ship.telemetry.latitude",
        "longitude": "ship.telemetry.longitude",
    }
    targets.update(aliases)
    return targets


@dataclass(frozen=True)
class ProjectionFieldDoc:
    """Metadata documenting a single materialized projection property."""

    field_name: str
    target_path: str
    type_annotation: str
    default_repr: str
    description: str


@dataclass(frozen=True)
class ProjectionDoc:
    """Metadata documenting a state projection dataclass."""

    projection_name: str
    accessor: str
    description: str
    fields: list[ProjectionFieldDoc]


def inspect_projection_metadata() -> list[ProjectionDoc]:
    """Inspects all state projection dataclasses on ClientStateProjection and
    extracts field names, type annotations, defaults, and doc metadata.
    """
    from ed_fleet_client.core.domain.state.models import (
        ClientStateProjection,
        LocationProjection,
        SessionProjection,
        ShipProjection,
    )

    docs: list[ProjectionDoc] = []
    classes = [
        ("LocationProjection", "client.location", LocationProjection),
        ("SessionProjection", "client.session", SessionProjection),
        ("ShipProjection", "client.ship", ShipProjection),
        ("ClientStateProjection", "client.state", ClientStateProjection),
    ]

    for cls_name, accessor, cls_type in classes:
        cls_doc = (cls_type.__doc__ or "").strip()
        field_docs: list[ProjectionFieldDoc] = []
        for f in fields(cls_type):
            if f.name in ("__post_init__",):
                continue
            default_val = f.default
            if default_val is dataclasses.MISSING:
                if f.default_factory is not dataclasses.MISSING:
                    default_repr = "<computed>"
                else:
                    default_repr = ""
            elif isinstance(default_val, str):
                default_repr = f'"{default_val}"' if default_val else '""'
            else:
                default_repr = repr(default_val)

            desc = f.metadata.get("description", "")
            type_str = str(f.type)
            target_path = (
                f"{accessor.split('.')[-1]}.{f.name}"
                if accessor != "client.state"
                else f"state.{f.name}"
            )

            field_docs.append(
                ProjectionFieldDoc(
                    field_name=f.name,
                    target_path=target_path,
                    type_annotation=type_str,
                    default_repr=default_repr,
                    description=desc,
                )
            )

        docs.append(
            ProjectionDoc(
                projection_name=cls_name,
                accessor=accessor,
                description=cls_doc,
                fields=field_docs,
            )
        )

    return docs
