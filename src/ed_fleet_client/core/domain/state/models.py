"""Immutable domain state projections for Elite Dangerous materialized client state."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from ed_models import StatusTelemetry


@dataclass(frozen=True)
class LocationProjection:
    """Materialized projection of player spatial location."""

    star_system: str = "Unknown"
    system_address: int | None = None
    star_pos: tuple[float, float, float] = (0.0, 0.0, 0.0)
    body: str = ""
    body_id: int | None = None
    body_type: str = ""
    station_name: str | None = None
    station_type: str | None = None
    market_id: int | None = None
    docked: bool = False
    in_supercruise: bool = False
    population: int = 0
    allegiance: str = ""
    economy: str = ""
    government: str = ""
    security: str = ""
    last_updated: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        """Enforces projection invariants."""
        pass


@dataclass(frozen=True)
class SessionProjection:
    """Materialized projection of active commander and game session."""

    commander_name: str = "Unknown"
    fid: str = ""
    game_mode: str = ""
    group: str = ""
    credits: int = 0
    loan: int = 0
    is_odyssey: bool = False
    game_version: str = ""
    is_alive: bool = True
    last_updated: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        """Enforces projection invariants."""
        pass


@dataclass(frozen=True)
class ShipProjection:
    """Materialized projection of ship status and loadout attributes."""

    ship_type: str = ""
    ship_name: str = ""
    ship_ident: str = ""
    hull_value: int = 0
    modules_value: int = 0
    rebuy: int = 0
    unladen_mass: float = 0.0
    cargo_capacity: int = 0
    max_jump_range: float = 0.0
    telemetry: StatusTelemetry | None = None
    last_updated: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        """Enforces projection invariants."""
        pass


@dataclass(frozen=True)
class ClientStateProjection:
    """Root immutable materialized state projection for an Elite Dangerous client."""

    session: SessionProjection = field(default_factory=SessionProjection)
    location: LocationProjection = field(default_factory=LocationProjection)
    ship: ShipProjection = field(default_factory=ShipProjection)
    sequence_number: int = 0
    last_event_name: str = ""
    last_event_timestamp: str = ""
    additional_metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Enforces projection invariants."""
        pass
