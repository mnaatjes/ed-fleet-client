"""Derived domain events produced by ed-services calculations."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from ed_models import JournalEvent


@dataclass
class NavBearingUpdated(JournalEvent):
    """Event emitted when ship geodetic bearing to a surface destination is recomputed."""

    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    event: str = "NavBearingUpdated"
    destination_name: str = ""
    bearing_deg: float = 0.0
    distance_km: float = 0.0
    heading_deg: float | None = None
    deflection_deg: float | None = None

    def __post_init__(self) -> None:
        """Enforces entity invariants."""
        pass


@dataclass
class NavDistanceUpdated(JournalEvent):
    """Event emitted when relative surface distance to a target is recomputed."""

    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    event: str = "NavDistanceUpdated"
    destination_name: str = ""
    distance_km: float = 0.0
    altitude_m: float | None = None

    def __post_init__(self) -> None:
        """Enforces entity invariants."""
        pass


@dataclass
class TargetLockedUpdated(JournalEvent):
    """Event emitted when targeted vessel or navigation destination lock updates."""

    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    event: str = "TargetLockedUpdated"
    locked: bool = False
    target_type: str = "Unknown"  # "Ship", "Station", "Body", "Settlement"
    target_name: str = ""
    pilot_name: str = ""
    ship_model: str = ""
    shield_health: float | None = None
    hull_health: float | None = None
    legal_status: str = ""

    def __post_init__(self) -> None:
        """Enforces entity invariants."""
        pass


@dataclass
class RouteProgressUpdated(JournalEvent):
    """Event emitted when hyperspace jump target or remaining jumps change."""

    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    event: str = "RouteProgressUpdated"
    destination_system: str = ""
    star_class: str = ""
    remaining_jumps: int = 0
    distance_ly: float | None = None

    def __post_init__(self) -> None:
        """Enforces entity invariants."""
        pass


@dataclass
class OrbitalBodyRecord:
    """Canonical Keplerian orbital elements cached for an astronomical body."""

    body_id: int
    body_name: str
    semi_major_axis_m: float
    eccentricity: float
    orbital_inclination_deg: float
    periapsis_deg: float
    ascending_node_deg: float
    mean_anomaly_deg: float
    orbital_period_s: float
    epoch_timestamp: str

    def __post_init__(self) -> None:
        """Enforces entity invariants."""
        pass


@dataclass
class BodyPositionPropagated(JournalEvent):
    """Event emitted when a body's 3D Cartesian position is calculated."""

    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    event: str = "BodyPositionPropagated"
    body_id: int = 0
    body_name: str = ""
    x_ls: float = 0.0
    y_ls: float = 0.0
    z_ls: float = 0.0
    distance_from_barycenter_ls: float = 0.0

    def __post_init__(self) -> None:
        """Enforces entity invariants."""
        pass


@dataclass
class PerformanceMetricsUpdated(JournalEvent):
    """Event emitted when live ship mass, jump range, or fuel burn rate updates."""

    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    event: str = "PerformanceMetricsUpdated"
    total_mass_t: float = 0.0
    max_jump_range_ly: float = 0.0
    fuel_burn_rate_t_per_hr: float = 0.0
    remaining_flight_hours: float | None = None

    def __post_init__(self) -> None:
        """Enforces entity invariants."""
        pass


@dataclass
class CombatDiagnosticsUpdated(JournalEvent):
    """Event emitted when real-time combat engagement DPS or TTK is recomputed."""

    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    event: str = "CombatDiagnosticsUpdated"
    target_dps: float = 0.0
    target_ttk_s: float | None = None
    incoming_dps: float = 0.0
    player_ttd_s: float | None = None
    sys_pip_damage_resistance: float = 0.0

    def __post_init__(self) -> None:
        """Enforces entity invariants."""
        pass


@dataclass
class HabitableZoneEvaluated(JournalEvent):
    """Event emitted when stellar habitable zone boundaries are calculated."""

    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    event: str = "HabitableZoneEvaluated"
    star_name: str = ""
    luminosity_solar: float = 0.0
    habitable_inner_au: float = 0.0
    habitable_outer_au: float = 0.0
    habitable_inner_ls: float = 0.0
    habitable_outer_ls: float = 0.0
    in_habitable_zone: bool = False
    planet_name: str | None = None

    def __post_init__(self) -> None:
        """Enforces entity invariants."""
        pass
