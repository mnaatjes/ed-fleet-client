"""Metadata domain models and response DTOs for ed-telemetry endpoints."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum


class TelemetryPlane(StrEnum):
    """Architectural resource plane defined by ed-telemetry."""

    STATE = "state"
    STATUS = "status"
    SNAPSHOTS = "snapshots"
    JOURNAL = "journal"
    SYSTEM = "system"
    UNKNOWN = "unknown"

    @classmethod
    def from_header(cls, value: str | None) -> TelemetryPlane:
        """Map raw X-Telemetry-Plane header value to canonical enum."""
        if not value:
            return cls.UNKNOWN
        clean = value.strip().lower()
        for member in cls:
            if member.value == clean:
                return member
        return cls.UNKNOWN


class TelemetrySource(StrEnum):
    """Storage origin declaring whether data was served from memory or SQLite WAL."""

    MEMORY_BUFFER = "memory-buffer"
    SQLITE_WAL = "sqlite-wal"
    UNKNOWN = "unknown"

    @classmethod
    def from_header(cls, value: str | None) -> TelemetrySource:
        """Map raw X-Telemetry-Source header value to canonical enum."""
        if not value:
            return cls.UNKNOWN
        clean = value.strip().lower()
        for member in cls:
            if member.value == clean:
                return member
        return cls.UNKNOWN


@dataclass(frozen=True)
class EndpointMetadata:
    """Hydrated HTTP-level and domain metadata captured from ed-telemetry response."""

    endpoint_url: str
    status_code: int
    plane: TelemetryPlane
    source: TelemetrySource
    etag: str | None = None
    content_type: str | None = None
    latency_ms: float = 0.0
    headers: Mapping[str, str] = field(default_factory=dict)

    @property
    def is_cached_candidate(self) -> bool:
        """True if response included an ETag usable with If-None-Match."""
        return self.etag is not None


@dataclass(frozen=True)
class TelemetryResponse[T]:
    """Unified boundary DTO encapsulating hydrated endpoint metadata and deserialized payload."""

    metadata: EndpointMetadata
    raw_payload: bytes
    data: T

    @property
    def text(self) -> str:
        """Decodes raw payload as UTF-8 string."""
        return self.raw_payload.decode("utf-8", errors="replace")


@dataclass(frozen=True)
class TelemetryConnectionConfig:
    """Connection parameters for communicating with an ed-telemetry server instance."""

    host: str = "192.168.1.214"
    port: int = 8080
    api_key: str | None = None
    default_path: str = "/api/v1/state"
    timeout: float = 10.0

    @property
    def base_url(self) -> str:
        """Constructs base HTTP URL."""
        return f"http://{self.host}:{self.port}"

    def build_url(self, path: str | None = None) -> str:
        """Constructs absolute URL for a given resource path."""
        target = path if path is not None else self.default_path
        if not target.startswith("/"):
            target = f"/{target}"
        return f"{self.base_url}{target}"
