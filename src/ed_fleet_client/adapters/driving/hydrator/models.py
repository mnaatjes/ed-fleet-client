"""Domain models and consolidated state containers for hydrated telemetry."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from ed_models import JournalEvent, StatusTelemetry

from ed_fleet_client.adapters.driven.telemetry_http import EndpointMetadata


@dataclass(frozen=True)
class ResilientSnapshotModel:
    """Resilient companion snapshot model preserving unknown fields (RISK-03)."""

    target_name: str = ""
    exists: bool = True
    is_live_session: bool = False
    timestamp: str | None = None
    raw_hash: str | None = None
    extra: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def from_raw(cls, name: str, raw: Mapping[str, Any]) -> ResilientSnapshotModel:
        known = {"target_name", "exists", "is_live_session", "timestamp", "raw_hash"}
        extra = {k: v for k, v in raw.items() if k not in known}
        return cls(
            target_name=str(raw.get("target_name", name)),
            exists=bool(raw.get("exists", True)),
            is_live_session=bool(raw.get("is_live_session", False)),
            timestamp=raw.get("timestamp"),
            raw_hash=raw.get("raw_hash"),
            extra=extra,
        )


@dataclass(frozen=True)
class RawSnapshotRecord:
    """Raw auxiliary file snapshot container before entity mapping."""

    target_name: str
    exists: bool
    is_live_session: bool
    timestamp: str | None
    raw_hash: str | None
    data: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class HydratedTelemetryState:
    """Strongly typed domain state consolidated from GET /api/v1/state."""

    state_sequence: int
    timestamp: str
    active_journal: str | None
    status: StatusTelemetry | None
    latest_event: JournalEvent | None
    raw_snapshots: Mapping[str, RawSnapshotRecord] = field(default_factory=dict)
    metadata: EndpointMetadata | None = None

    @property
    def has_active_session(self) -> bool:
        """True if game status indicates an active live session."""
        return self.status is not None


@dataclass(frozen=True)
class HydratedEventRecord:
    """Domain record representing an individual journal event with telemetry envelope metadata."""

    event_id: str | int | None
    topic: str
    timestamp: datetime | str
    event: JournalEvent
    raw_hash: str | None = None
    metadata: EndpointMetadata | None = None
