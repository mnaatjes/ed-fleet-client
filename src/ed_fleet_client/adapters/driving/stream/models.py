"""Models for telemetry stream monitoring."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class StreamMonitorConfig:
    """Configuration for telemetry stream ingestion."""

    poll_interval_seconds: float = 0.5
    reconnect_delay_seconds: float = 2.0
    filter_historical: bool = True
    since_timestamp: str | None = None


@dataclass(frozen=True)
class StreamFrame:
    """Immutable wrapper representing a single raw telemetry frame."""

    source: str
    payload: dict[str, Any] = field(default_factory=dict)
