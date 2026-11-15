"""Driving hydrator adapter converting raw telemetry payloads into typed ed-models."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from ed_models import (
    JournalEvent,
    StatusFlags,
    StatusFlags2,
    StatusTelemetry,
    create_domain_facade,
    parse_journal_event,
)

from ed_fleet_client.adapters.driven.telemetry_http import TelemetryResponse

from .models import (
    HydratedEventRecord,
    HydratedTelemetryState,
    RawSnapshotRecord,
)


class TelemetryDomainHydrator:
    """Transforms raw or parsed payloads from ed-telemetry endpoints into typed ed-models."""

    def __init__(self) -> None:
        self._facade = create_domain_facade()

    def hydrate_status(self, raw: Mapping[str, Any] | str) -> StatusTelemetry | None:
        """Hydrates Status.json bitfields and telemetry values into ed_models.StatusTelemetry."""
        data: dict[str, Any]
        if isinstance(raw, str):
            try:
                data = json.loads(raw)
            except (json.JSONDecodeError, TypeError):
                return None
        elif isinstance(raw, Mapping):
            if "raw_payload" in raw and isinstance(raw["raw_payload"], str):
                try:
                    data = json.loads(raw["raw_payload"])
                except (json.JSONDecodeError, TypeError):
                    return None
            else:
                data = dict(raw)
        else:
            return None

        flags = int(data.get("Flags", 0))
        flags2 = int(data.get("Flags2", 0))

        raw_pips = data.get("Pips", [4, 4, 4])
        if isinstance(raw_pips, list) and len(raw_pips) >= 3:
            pips = (int(raw_pips[0]), int(raw_pips[1]), int(raw_pips[2]))
        else:
            pips = (4, 4, 4)

        fuel = data.get("Fuel", {})
        fuel_main = float(fuel.get("FuelMain", 0.0)) if isinstance(fuel, dict) else 0.0
        fuel_reservoir = float(fuel.get("FuelReservoir", 0.0)) if isinstance(fuel, dict) else 0.0
        cargo = int(data.get("Cargo", 0))
        legal_state = str(data.get("LegalState", "Clean"))

        lat = (
            float(data["Latitude"]) if "Latitude" in data and data["Latitude"] is not None else None
        )
        lon = (
            float(data["Longitude"])
            if "Longitude" in data and data["Longitude"] is not None
            else None
        )
        alt = (
            float(data["Altitude"]) if "Altitude" in data and data["Altitude"] is not None else None
        )
        hdg = float(data["Heading"]) if "Heading" in data and data["Heading"] is not None else None
        radius = (
            float(data["PlanetRadius"])
            if "PlanetRadius" in data and data["PlanetRadius"] is not None
            else None
        )
        body_name = (
            str(data["BodyName"]) if "BodyName" in data and data["BodyName"] is not None else None
        )

        additional: dict[str, Any] = {}
        if "Destination" in data and isinstance(data["Destination"], dict):
            additional["Destination"] = dict(data["Destination"])

        return StatusTelemetry(
            flags=StatusFlags(flags),
            flags2=StatusFlags2(flags2),
            pips=pips,
            fuel_main=fuel_main,
            fuel_reservoir=fuel_reservoir,
            cargo=cargo,
            legal_state=legal_state,
            latitude=lat,
            longitude=lon,
            altitude=alt,
            heading=hdg,
            planet_radius=radius,
            body_name=body_name,
            additional_fields=additional,
        )

    def hydrate_journal_event(self, raw: Mapping[str, Any] | str) -> JournalEvent | None:
        """Hydrates a Frontier Journal event payload into a typed ed_models.JournalEvent."""
        data: dict[str, Any]
        if isinstance(raw, str):
            try:
                data = json.loads(raw)
            except (json.JSONDecodeError, TypeError):
                return None
        elif isinstance(raw, Mapping):
            if "payload_json" in raw and isinstance(raw["payload_json"], str):
                try:
                    data = json.loads(raw["payload_json"])
                except (json.JSONDecodeError, TypeError):
                    return None
            else:
                data = dict(raw)
        else:
            return None

        if "event" not in data:
            return None

        return parse_journal_event(data)

    def hydrate_event(self, payload: Mapping[str, Any] | str) -> JournalEvent | None:
        """Alias for hydrate_journal_event."""
        return self.hydrate_journal_event(payload)

    def hydrate_snapshot(self, name: str, raw: dict[str, Any]) -> RawSnapshotRecord:
        """Hydrates a named companion snapshot payload with extra='allow' resilience."""
        from .models import ResilientSnapshotModel

        validated = ResilientSnapshotModel.from_raw(name, raw)
        return RawSnapshotRecord(
            target_name=validated.target_name,
            exists=validated.exists,
            is_live_session=validated.is_live_session,
            timestamp=validated.timestamp,
            raw_hash=validated.raw_hash,
            data={**dict(raw), **dict(validated.extra)},
        )

    def hydrate_state(self, response: TelemetryResponse[Any]) -> HydratedTelemetryState:
        """Hydrates a GET /api/v1/state response DTO into HydratedTelemetryState."""
        data = response.data if isinstance(response.data, Mapping) else {}
        raw_status = data.get("game_status")
        status = (
            self.hydrate_status(raw_status)
            if isinstance(raw_status, Mapping) and raw_status.get("exists", True)
            else None
        )
        raw_event = data.get("latest_journal_event")
        latest_event = (
            self.hydrate_journal_event(raw_event) if isinstance(raw_event, Mapping) else None
        )

        snapshots: dict[str, RawSnapshotRecord] = {}
        raw_snaps = data.get("snapshots", {})
        if isinstance(raw_snaps, Mapping):
            for snap_name, snap_body in raw_snaps.items():
                if isinstance(snap_body, Mapping):
                    snapshots[str(snap_name)] = self.hydrate_snapshot(
                        str(snap_name), dict(snap_body)
                    )

        return HydratedTelemetryState(
            state_sequence=int(data.get("state_sequence", 0)),
            timestamp=str(data.get("timestamp", "")),
            active_journal=data.get("active_journal"),
            status=status,
            latest_event=latest_event,
            raw_snapshots=snapshots,
            metadata=response.metadata,
        )

    def hydrate_event_record(self, raw: Mapping[str, Any]) -> HydratedEventRecord | None:
        """Hydrates an enveloped journal event record."""
        event = self.hydrate_journal_event(raw)
        if event is None:
            return None
        return HydratedEventRecord(
            event_id=raw.get("event_id"),
            topic=str(raw.get("topic", "telemetry.journal")),
            timestamp=str(raw.get("timestamp", getattr(event, "timestamp", ""))),
            event=event,
            raw_hash=raw.get("raw_hash"),
        )
