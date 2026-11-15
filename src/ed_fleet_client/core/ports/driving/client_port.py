"""Driving port contract for the public EliteDangerousClient facade."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from ...domain.state.models import ClientStateProjection
from ..base import DrivingPort


@runtime_checkable
class ClientFacadePort(DrivingPort, Protocol):
    """Primary port defining the public client state and lifecycle interface."""

    @property
    def state(self) -> ClientStateProjection:
        """Returns the current immutable materialized client state projection."""
        ...

    async def connect(self) -> None:
        """Connects to the telemetry stream and begins state reduction."""
        ...

    async def disconnect(self) -> None:
        """Disconnects from the telemetry stream."""
        ...
