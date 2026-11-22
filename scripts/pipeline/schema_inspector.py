"""AST Schema reflection and property classification for ed-models."""

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
