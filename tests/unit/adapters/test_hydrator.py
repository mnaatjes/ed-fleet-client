"""Unit tests for TelemetryDomainHydrator driving adapter."""

from __future__ import annotations

import json

from ed_models import JournalEvent, StatusTelemetry

from ed_fleet_client.adapters.driven.telemetry_http import (
    EndpointMetadata,
    TelemetryPlane,
    TelemetryResponse,
    TelemetrySource,
)
from ed_fleet_client.adapters.driving.hydrator import (
    HydratedTelemetryState,
    TelemetryDomainHydrator,
)


def test_hydrate_status_entity() -> None:
    hydrator = TelemetryDomainHydrator()
    payload = {
        "Flags": 16842769,
        "Flags2": 0,
        "Pips": [4, 4, 4],
        "Fuel": {"FuelMain": 32.0, "FuelReservoir": 0.5},
        "Cargo": 4,
        "LegalState": "Clean",
    }
    status = hydrator.hydrate_status(payload)
    assert status is not None
    assert isinstance(status, StatusTelemetry)
    assert status.is_docked is True
    assert status.fuel_main == 32.0
    assert status.cargo == 4
    assert status.legal_state == "Clean"


def test_hydrate_journal_event_entity() -> None:
    hydrator = TelemetryDomainHydrator()
    payload = {
        "timestamp": "2026-11-08T12:00:00Z",
        "event": "FSDJump",
        "StarSystem": "Shinrarta Dezhra",
        "SystemAddress": 3932277478106,
        "StarPos": [55.71875, 17.59375, 27.15625],
    }
    event = hydrator.hydrate_journal_event(payload)
    assert event is not None
    assert isinstance(event, JournalEvent)


def test_hydrate_full_state_response() -> None:
    hydrator = TelemetryDomainHydrator()
    state_payload = {
        "state_sequence": 88,
        "timestamp": "2026-11-08T14:30:00+00:00",
        "active_journal": "Journal.2026-11-08T140000.01.log",
        "game_status": {
            "exists": True,
            "raw_payload": json.dumps({"Flags": 1, "Pips": [2, 8, 2], "Fuel": {"FuelMain": 16.0}}),
        },
        "snapshots": {
            "Market": {
                "target_name": "Market.json",
                "exists": True,
            }
        },
    }
    meta = EndpointMetadata(
        endpoint_url="http://127.0.0.1:8080/api/v1/state",
        status_code=200,
        plane=TelemetryPlane.STATE,
        source=TelemetrySource.MEMORY_BUFFER,
    )
    resp_dto = TelemetryResponse(
        metadata=meta,
        raw_payload=json.dumps(state_payload).encode("utf-8"),
        data=state_payload,
    )
    state = hydrator.hydrate_state(resp_dto)
    assert isinstance(state, HydratedTelemetryState)
    assert state.state_sequence == 88
    assert state.has_active_session is True
    assert "Market" in state.raw_snapshots
