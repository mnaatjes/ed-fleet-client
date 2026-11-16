"""Unit test for stream SSE payload hydration and reactive event dispatch."""

from __future__ import annotations

import json
from typing import Any

from ed_models.core.domain.events import FSDTarget

from ed_fleet_client.bootstrap.container import create_client


def test_stream_monitor_dispatches_sse_payload_to_subscribers() -> None:
    client = create_client()
    received_events: list[FSDTarget] = []

    client.subscribe(FSDTarget, lambda ev: received_events.append(ev))

    # Simulate SSE frame received from ed-telemetry (with 'payload' key containing JSON string)
    fsd_target_journal = {
        "timestamp": "2026-11-16T03:10:00Z",
        "event": "FSDTarget",
        "Name": "Shinrarta Dezhra",
        "SystemAddress": 3932277478106,
        "StarClass": "A",
        "RemainingJumpsInRoute": 2,
    }
    sse_frame: dict[str, Any] = {
        "topic": "telemetry.journal",
        "timestamp": "2026-11-16T03:10:00.123456+00:00",
        "payload": json.dumps(fsd_target_journal) + "\r\n",
    }

    # Simulate arrival of frame via stream monitor callback
    client._handle_raw_event(sse_frame)

    assert len(received_events) == 1
    event = received_events[0]
    assert isinstance(event, FSDTarget)
    assert event.Name == "Shinrarta Dezhra"
    assert event.RemainingJumpsInRoute == 2
    assert event.StarClass == "A"
