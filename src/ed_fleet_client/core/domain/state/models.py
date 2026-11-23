"""Immutable domain state projections for Elite Dangerous materialized client state."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from ed_models import StatusTelemetry


@dataclass(frozen=True)
class LocationProjection:
    """Materialized projection of player spatial location."""

    star_system: str = field(
        default="Unknown",
        metadata={"description": "Authoritative current star system name."},
    )
    system_address: int | None = field(
        default=None,
        metadata={"description": "Unique 64-bit Frontier system address hash."},
    )
    star_pos: tuple[float, float, float] = field(
        default=(0.0, 0.0, 0.0),
        metadata={"description": "Galactic 3D Cartesian coordinates (x, y, z) in light years."},
    )
    body: str = field(
        default="",
        metadata={"description": "Current celestial body or star name."},
    )
    body_id: int | None = field(
        default=None,
        metadata={"description": "System-unique numerical identifier for current celestial body."},
    )
    body_type: str = field(
        default="",
        metadata={"description": "Celestial body classification (e.g. Star, Planet, Station)."},
    )
    station_name: str | None = field(
        default=None,
        metadata={"description": "Name of the starport, outpost, or carrier currently docked at."},
    )
    station_type: str | None = field(
        default=None,
        metadata={"description": "Type of station currently docked at (e.g. Coriolis, Outpost)."},
    )
    market_id: int | None = field(
        default=None,
        metadata={"description": "Unique 64-bit market identifier for local commodity exchange."},
    )
    docked: bool = field(
        default=False,
        metadata={"description": "True if vessel is currently docked at a facility."},
    )
    in_supercruise: bool = field(
        default=False,
        metadata={"description": "True if vessel is currently flying in supercruise regime."},
    )
    population: int = field(
        default=0,
        metadata={"description": "Total registered population of the current star system."},
    )
    allegiance: str = field(
        default="",
        metadata={"description": "Superpower allegiance of the current system (e.g. Federation)."},
    )
    economy: str = field(
        default="",
        metadata={"description": "Primary economic activity of the current system."},
    )
    government: str = field(
        default="",
        metadata={"description": "Government archetype of the current system (e.g. Democracy)."},
    )
    security: str = field(
        default="",
        metadata={"description": "System law enforcement security level (e.g. High, Anarchy)."},
    )
    last_updated: datetime = field(
        default_factory=lambda: datetime.now(UTC),
        metadata={"description": "UTC timestamp of the last applied state reduction update."},
    )

    def __post_init__(self) -> None:
        """Enforces projection invariants."""
        pass


@dataclass(frozen=True)
class SessionProjection:
    """Materialized projection of active commander and game session."""

    commander_name: str = field(
        default="Unknown",
        metadata={"description": "Active commander in-game callsign or name."},
    )
    fid: str = field(
        default="",
        metadata={"description": "Frontier customer account identification hash."},
    )
    game_mode: str = field(
        default="",
        metadata={"description": "Active game mode (Open, Group, or Solo)."},
    )
    group: str = field(
        default="",
        metadata={"description": "Private group name if playing in Group mode."},
    )
    credits: int = field(
        default=0,
        metadata={"description": "Total liquid credit balance available to the commander."},
    )
    loan: int = field(
        default=0,
        metadata={"description": "Active debt or insurance loan outstanding balance."},
    )
    is_odyssey: bool = field(
        default=False,
        metadata={"description": "True if current game session is running on the Odyssey client."},
    )
    game_version: str = field(
        default="",
        metadata={"description": "Frontier game build and version release identifier string."},
    )
    is_alive: bool = field(
        default=True,
        metadata={"description": "True if the commander vessel/avatar is currently alive."},
    )
    last_updated: datetime = field(
        default_factory=lambda: datetime.now(UTC),
        metadata={"description": "UTC timestamp of the last applied session state update."},
    )

    def __post_init__(self) -> None:
        """Enforces projection invariants."""
        pass


@dataclass(frozen=True)
class ShipProjection:
    """Materialized projection of ship status and loadout attributes."""

    ship_type: str = field(
        default="",
        metadata={"description": "Vessel model and chassis identifier (e.g. 'krait_mkii')."},
    )
    ship_id: int | None = field(
        default=None,
        metadata={"description": "Commander shipyard instance ID for the active vessel."},
    )
    ship_name: str = field(
        default="",
        metadata={"description": "Custom user-given ship name."},
    )
    ship_ident: str = field(
        default="",
        metadata={"description": "Custom tail/hull registration callsign (e.g. 'DSV-04')."},
    )
    hull_value: int = field(
        default=0,
        metadata={"description": "Base hull purchase credit valuation."},
    )
    hull_health: float = field(
        default=1.0,
        metadata={"description": "Structural integrity proportion of vessel hull (0.0 to 1.0)."},
    )
    modules_value: int = field(
        default=0,
        metadata={"description": "Total credit valuation of all fitted modules and hardpoints."},
    )
    rebuy: int = field(
        default=0,
        metadata={"description": "Total insurance replacement deductible cost."},
    )
    unladen_mass: float = field(
        default=0.0,
        metadata={"description": "Unladen dry hull and module mass in metric tonnes."},
    )
    cargo_capacity: int = field(
        default=0,
        metadata={"description": "Maximum cargo rack capacity in standard metric tonnes."},
    )
    max_jump_range: float = field(
        default=0.0,
        metadata={"description": "Maximum single-jump hyperdrive range in light years."},
    )
    telemetry: StatusTelemetry | None = field(
        default=None,
        metadata={"description": "Latest real-time cockpit StatusTelemetry snapshot frame."},
    )
    last_updated: datetime = field(
        default_factory=lambda: datetime.now(UTC),
        metadata={"description": "UTC timestamp of the last applied ship loadout update."},
    )

    def __post_init__(self) -> None:
        """Enforces projection invariants."""
        pass


@dataclass(frozen=True)
class ClientStateProjection:
    """Root immutable materialized state projection for an Elite Dangerous client."""

    session: SessionProjection = field(
        default_factory=SessionProjection,
        metadata={"description": "Commander and game session projection state."},
    )
    location: LocationProjection = field(
        default_factory=LocationProjection,
        metadata={"description": "Spatial location and star system projection state."},
    )
    ship: ShipProjection = field(
        default_factory=ShipProjection,
        metadata={"description": "Active ship hardware, loadout, and cockpit telemetry state."},
    )
    sequence_number: int = field(
        default=0,
        metadata={"description": "Monotonically increasing counter of processed events."},
    )
    last_event_name: str = field(
        default="",
        metadata={"description": "Name of the most recently processed journal/telemetry event."},
    )
    last_event_timestamp: str = field(
        default="",
        metadata={"description": "Timestamp string emitted on the most recent event packet."},
    )
    additional_metadata: dict[str, Any] = field(
        default_factory=dict,
        metadata={"description": "Extensible metadata dictionary for companion extensions."},
    )

    def __post_init__(self) -> None:
        """Enforces projection invariants."""
        pass
