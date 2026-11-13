"""Unit tests for TelemetryEventDispatcher."""

from __future__ import annotations

import pytest
from ed_models import JournalEvent, StatusTelemetry
from ed_models.core.domain.events import FSDJump, Location, Music, ReceiveText

from ed_fleet_client.core.domain.dispatcher.dispatcher import TelemetryEventDispatcher


def test_dispatcher_sync_registration_and_dispatch() -> None:
    dispatcher = TelemetryEventDispatcher()
    received_jumps: list[FSDJump] = []

    @dispatcher.on(FSDJump)
    def handle_jump(event: FSDJump) -> None:
        received_jumps.append(event)

    jump = FSDJump(
        timestamp="2026-11-09T03:45:00Z",
        event="FSDJump",
        StarSystem="Shinrarta Dezhra",
    )

    result = dispatcher.dispatch(jump)
    assert result.event_name == "FSDJump"
    assert result.total_matched == 1
    assert result.executed_count == 1
    assert not result.has_errors
    assert len(received_jumps) == 1
    assert received_jumps[0].StarSystem == "Shinrarta Dezhra"


def test_dispatcher_transient_event_handling() -> None:
    dispatcher = TelemetryEventDispatcher()
    music_tracks: list[str] = []

    @dispatcher.on(Music)
    def handle_music(event: Music) -> None:
        music_tracks.append(getattr(event, "MusicTrack", "UnknownTrack"))

    music = Music(
        timestamp="2026-11-09T03:46:00Z",
        event="Music",
        MusicTrack="Supercruise",
    )

    result = dispatcher.dispatch(music)
    assert result.event_name == "Music"
    assert result.executed_count == 1
    assert music_tracks == ["Supercruise"]


def test_dispatcher_status_telemetry_handling() -> None:
    dispatcher = TelemetryEventDispatcher()
    received_status: list[StatusTelemetry] = []

    @dispatcher.on(StatusTelemetry)
    def handle_status(event: StatusTelemetry) -> None:
        received_status.append(event)

    status = StatusTelemetry(cargo=10, fuel_main=32.0)
    result = dispatcher.dispatch(status)
    assert result.event_name == "StatusTelemetry"
    assert result.executed_count == 1
    assert len(received_status) == 1
    assert received_status[0].cargo == 10


def test_dispatcher_polymorphic_wildcard_matching() -> None:
    dispatcher = TelemetryEventDispatcher()
    all_journal_events: list[JournalEvent] = []

    # Wildcard listener: listens for any JournalEvent
    @dispatcher.on(JournalEvent)
    def catch_all(event: JournalEvent) -> None:
        all_journal_events.append(event)

    jump = FSDJump(timestamp="2026-11-09T03:47:00Z", event="FSDJump", StarSystem="Sol")
    chat = ReceiveText(timestamp="2026-11-09T03:47:05Z", event="ReceiveText", Message="Fly safe")

    dispatcher.dispatch(jump)
    dispatcher.dispatch(chat)

    assert len(all_journal_events) == 2
    assert all_journal_events[0].event == "FSDJump"
    assert all_journal_events[1].event == "ReceiveText"


def test_dispatcher_error_isolation() -> None:
    dispatcher = TelemetryEventDispatcher()
    good_handler_called = False

    @dispatcher.on(Location)
    def failing_handler(event: Location) -> None:
        raise ValueError("Simulated callback explosion")

    @dispatcher.on(Location)
    def good_handler(event: Location) -> None:
        nonlocal good_handler_called
        good_handler_called = True

    loc = Location(timestamp="2026-11-09T03:48:00Z", event="Location", StarSystem="Achenar")
    result = dispatcher.dispatch(loc)

    assert result.total_matched == 2
    assert result.executed_count == 1
    assert result.has_errors
    assert len(result.failures) == 1
    assert result.failures[0].error_type == "ValueError"
    assert result.failures[0].error_message == "Simulated callback explosion"
    assert good_handler_called is True


def test_dispatcher_unsubscription_and_clear() -> None:
    dispatcher = TelemetryEventDispatcher()
    calls = 0

    def counter(event: Music) -> None:
        nonlocal calls
        calls += 1

    sub = dispatcher.subscribe(Music, counter)
    assert dispatcher.subscription_count == 1

    dispatcher.dispatch(Music(timestamp="", event="Music"))
    assert calls == 1

    # Unsubscribe token
    removed = dispatcher.unsubscribe(sub)
    assert removed is True
    assert dispatcher.subscription_count == 0

    dispatcher.dispatch(Music(timestamp="", event="Music"))
    assert calls == 1

    # Clear test
    dispatcher.subscribe(Music, counter)
    assert dispatcher.subscription_count == 1
    dispatcher.clear()
    assert dispatcher.subscription_count == 0


@pytest.mark.asyncio
async def test_dispatcher_async_dispatch() -> None:
    dispatcher = TelemetryEventDispatcher()
    async_received: list[str] = []

    @dispatcher.on(ReceiveText)
    async def async_handler(event: ReceiveText) -> None:
        async_received.append(getattr(event, "Message", ""))

    msg = ReceiveText(
        timestamp="2026-11-09T03:49:00Z",
        event="ReceiveText",
        Message="Async ping",
    )
    result = await dispatcher.dispatch_async(msg)

    assert result.executed_count == 1
    assert async_received == ["Async ping"]
