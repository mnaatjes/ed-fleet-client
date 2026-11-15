"""Driving port contract for hydrating raw telemetry payloads into domain entities."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from ..base import DrivingPort


@runtime_checkable
class HydratorPort(DrivingPort, Protocol):
    """Primary port for hydrating raw JSON payloads into typed domain models."""

    def hydrate_journal_event(self, raw: dict[str, Any]) -> Any:
        """Hydrates a raw journal event dictionary into a typed JournalEvent."""
        ...

    def hydrate_status(self, raw: dict[str, Any]) -> Any:
        """Hydrates a raw Status.json payload into a typed StatusTelemetry."""
        ...

    def hydrate_snapshot(self, name: str, raw: dict[str, Any]) -> Any:
        """Hydrates a named companion snapshot payload (e.g., Market, Cargo)."""
        ...
