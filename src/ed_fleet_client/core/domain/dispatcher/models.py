"""Dataclasses and types for ed-fleet-client observer engine."""

from __future__ import annotations

import uuid
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from ed_models import JournalEvent, StatusTelemetry

# Union of supported domain event payload types
TelemetryEvent = JournalEvent | StatusTelemetry

# Signature for event handler callbacks (accepts specific event, returns anything or coroutine)
EventHandler = Callable[[Any], None | Awaitable[None]]


@dataclass(frozen=True)
class Subscription:
    """Handle representing an active event subscription token."""

    subscription_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: type[Any] = object
    is_async: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        """Enforces entity invariants."""
        pass


@dataclass(frozen=True)
class HandlerFailure:
    """Details of an exception raised inside an event handler."""

    subscription_id: str
    event_type: str
    handler_name: str
    error_type: str
    error_message: str
    raised_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        """Enforces entity invariants."""
        pass


@dataclass(frozen=True)
class DispatchResult:
    """Execution telemetry and outcome of a dispatch invocation."""

    event_name: str
    total_matched: int
    executed_count: int
    failures: list[HandlerFailure] = field(default_factory=list)
    dispatched_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        """Enforces entity invariants."""
        pass

    @property
    def has_errors(self) -> bool:
        return len(self.failures) > 0
