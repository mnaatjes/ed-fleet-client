"""Unit tests for TelemetryStateEngine."""

from __future__ import annotations

from ed_models import StatusTelemetry
from ed_models.core.domain.events import FSDJump, LoadGame

from ed_fleet_client.core.domain.state.engine import TelemetryStateEngine


def test_state_engine_lifecycle_and_accumulation() -> None:
    engine = TelemetryStateEngine()
    assert engine.current.sequence_number == 0
    assert engine.location.star_system == "Unknown"
    assert engine.session.commander_name == "Unknown"

    # Step 1: Session initialization
    load_ev = LoadGame(
        timestamp="2026-11-09T03:00:00Z",
        event="LoadGame",
        Commander="Adulantis",
        FID="F5611068",
        Credits=123456789,
    )
    engine.apply(load_ev)
    assert engine.current.sequence_number == 1
    assert engine.session.commander_name == "Adulantis"
    assert engine.session.credits == 123456789

    # Step 2: Location jump
    jump_ev = FSDJump(
        timestamp="2026-11-09T03:05:00Z",
        event="FSDJump",
        StarSystem="Achenar",
        Body="Achenar 3",
        Population=15000000000,
    )
    engine.apply(jump_ev)
    assert engine.current.sequence_number == 2
    assert engine.location.star_system == "Achenar"
    assert engine.location.body == "Achenar 3"
    # Session state preserved
    assert engine.session.commander_name == "Adulantis"

    # Step 3: Cockpit Status telemetry
    status = StatusTelemetry(fuel_main=32.0, cargo=12)
    engine.apply(status)
    assert engine.current.sequence_number == 3
    assert engine.ship.telemetry is not None
    assert engine.ship.telemetry.fuel_main == 32.0
    assert engine.ship.telemetry.cargo == 12

    # Step 4: Reset
    engine.reset()
    assert engine.current.sequence_number == 0
    assert engine.location.star_system == "Unknown"
