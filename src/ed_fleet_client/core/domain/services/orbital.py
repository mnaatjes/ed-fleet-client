"""Orbital mechanics engine solving Kepler's equations and celestial body propagation."""

from __future__ import annotations

import math
import threading
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

from ed_models.core.domain.events import FSDJump
from ed_models.core.domain.events.exploration.scan import ScanPlanet, ScanStar
from ed_models.core.domain.spatial.coordinates import Coordinates3D

from ..dispatcher import Subscription, TelemetryEventDispatcher
from ..state import ClientStateProjection
from .base import TelemetryService
from .models import BodyPositionPropagated, OrbitalBodyRecord

# Speed of light in meters per second
SPEED_OF_LIGHT_M_S = 299_792_458.0


def solve_kepler_equation(
    mean_anomaly_rad: float, eccentricity: float, tolerance: float = 1e-8, max_iter: int = 100
) -> float:
    """Solves Kepler's equation M = E - e*sin(E) for Eccentric Anomaly E using Newton-Raphson."""
    # Normalize M to [-pi, pi]
    m = (mean_anomaly_rad + math.pi) % (2.0 * math.pi) - math.pi

    # Initial guess
    e_anom = m if eccentricity < 0.8 else math.pi

    for _ in range(max_iter):
        f = e_anom - eccentricity * math.sin(e_anom) - m
        f_prime = 1.0 - eccentricity * math.cos(e_anom)
        delta = f / f_prime
        e_anom -= delta
        if abs(delta) < tolerance:
            break

    return e_anom


def propagate_keplerian_orbit(
    semi_major_axis_m: float,
    eccentricity: float,
    orbital_inclination_deg: float,
    periapsis_deg: float,
    ascending_node_deg: float,
    mean_anomaly_deg: float,
    orbital_period_s: float,
    epoch_timestamp_iso: str,
    target_time: datetime | None = None,
) -> Coordinates3D:
    """Propagates Keplerian orbital elements to 3D Cartesian coordinates (in light-seconds)."""
    if orbital_period_s <= 0:
        return Coordinates3D(x=0.0, y=0.0, z=0.0)

    t_now = target_time if target_time is not None else datetime.now(UTC)

    try:
        t_epoch = datetime.fromisoformat(epoch_timestamp_iso.replace("Z", "+00:00"))
    except Exception:
        t_epoch = t_now

    elapsed_s = (t_now - t_epoch).total_seconds()

    # 1. Calculate current Mean Anomaly M(t)
    n = (2.0 * math.pi) / orbital_period_s
    m0_rad = math.radians(mean_anomaly_deg)
    m_t = (m0_rad + n * elapsed_s) % (2.0 * math.pi)

    # 2. Solve for Eccentric Anomaly E
    e_anom = solve_kepler_equation(m_t, eccentricity)

    # 3. Calculate True Anomaly nu and orbital radius r
    sin_e = math.sin(e_anom)
    cos_e = math.cos(e_anom)
    sin_nu = (math.sqrt(max(0.0, 1.0 - eccentricity**2)) * sin_e) / (1.0 - eccentricity * cos_e)
    cos_nu = (cos_e - eccentricity) / (1.0 - eccentricity * cos_e)
    nu = math.atan2(sin_nu, cos_nu)

    r_m = semi_major_axis_m * (1.0 - eccentricity * cos_e)

    # 4. In-plane coordinates
    x_prime = r_m * math.cos(nu)
    y_prime = r_m * math.sin(nu)

    # 5. Rotate into 3D system space using orbital angles
    omega = math.radians(periapsis_deg)
    i = math.radians(orbital_inclination_deg)
    capital_omega = math.radians(ascending_node_deg)

    # Rotation matrix composition: Rz(-Omega) * Rx(-i) * Rz(-omega)
    cos_o = math.cos(omega)
    sin_o = math.sin(omega)
    cos_i = math.cos(i)
    sin_i = math.sin(i)
    cos_node = math.cos(capital_omega)
    sin_node = math.sin(capital_omega)

    # Transform coordinates
    p_x = cos_node * cos_o - sin_node * sin_o * cos_i
    p_y = sin_node * cos_o + cos_node * sin_o * cos_i
    p_z = sin_o * sin_i

    q_x = -cos_node * sin_o - sin_node * cos_o * cos_i
    q_y = -sin_node * sin_o + cos_node * cos_o * cos_i
    q_z = cos_o * sin_i

    x_3d_m = x_prime * p_x + y_prime * q_x
    y_3d_m = x_prime * p_y + y_prime * q_y
    z_3d_m = x_prime * p_z + y_prime * q_z

    # Convert meters to light-seconds
    x_ls = round(x_3d_m / SPEED_OF_LIGHT_M_S, 3)
    y_ls = round(y_3d_m / SPEED_OF_LIGHT_M_S, 3)
    z_ls = round(z_3d_m / SPEED_OF_LIGHT_M_S, 3)

    return Coordinates3D(x=x_ls, y=y_ls, z=z_ls)


class OrbitalMechanicsService(TelemetryService):
    """Provides astronomical ephemeris propagation and planetary tracking."""

    def __init__(
        self,
        state_accessor: Callable[[], ClientStateProjection],
        dispatcher: TelemetryEventDispatcher,
    ) -> None:
        self._lock = threading.RLock()
        self._bodies: dict[int, OrbitalBodyRecord] = {}
        self._subscriptions: list[Subscription] = []
        super().__init__(state_accessor, dispatcher)

    # =========================================================================
    # Pattern 1: State-Guarded Pull Methods
    # =========================================================================

    def get_body_position(
        self, body_id: int, at_time: datetime | None = None
    ) -> Coordinates3D | None:
        """Returns 3D Cartesian coordinates (in light-seconds) of a body relative to barycenter."""
        with self._lock:
            body = self._bodies.get(body_id)
            if not body:
                return None

            return propagate_keplerian_orbit(
                semi_major_axis_m=body.semi_major_axis_m,
                eccentricity=body.eccentricity,
                orbital_inclination_deg=body.orbital_inclination_deg,
                periapsis_deg=body.periapsis_deg,
                ascending_node_deg=body.ascending_node_deg,
                mean_anomaly_deg=body.mean_anomaly_deg,
                orbital_period_s=body.orbital_period_s,
                epoch_timestamp_iso=body.epoch_timestamp,
                target_time=at_time,
            )

    def get_interplanetary_distance_ls(
        self, body_id_a: int, body_id_b: int, at_time: datetime | None = None
    ) -> float | None:
        """Calculates Euclidean distance in light-seconds between two scanned celestial bodies."""
        pos_a = self.get_body_position(body_id_a, at_time)
        pos_b = self.get_body_position(body_id_b, at_time)
        if not pos_a or not pos_b:
            return None

        dx = pos_a.x - pos_b.x
        dy = pos_a.y - pos_b.y
        dz = pos_a.z - pos_b.z
        return round(math.sqrt(dx**2 + dy**2 + dz**2), 3)

    def get_periapsis_apoapsis_ls(self, body_id: int) -> tuple[float, float] | None:
        """Returns closest approach (periapsis) and furthest distance (apoapsis) in
        light-seconds.
        """
        with self._lock:
            body = self._bodies.get(body_id)
            if not body:
                return None

            a_ls = body.semi_major_axis_m / SPEED_OF_LIGHT_M_S
            e = body.eccentricity
            return (round(a_ls * (1.0 - e), 3), round(a_ls * (1.0 + e), 3))

    def list_bodies(self) -> list[dict[str, Any]]:
        """Returns summary records of all scanned bodies in the active system."""
        with self._lock:
            return [
                {
                    "body_id": b.body_id,
                    "body_name": b.body_name,
                    "semi_major_axis_ls": round(b.semi_major_axis_m / SPEED_OF_LIGHT_M_S, 2),
                    "eccentricity": round(b.eccentricity, 4),
                    "orbital_period_days": round(b.orbital_period_s / 86400.0, 2),
                }
                for b in self._bodies.values()
            ]

    # =========================================================================
    # Pattern 2: Reactive Stream Pipe
    # =========================================================================

    def _record_body(
        self,
        *,
        body_id: int,
        body_name: str,
        semi_major_axis: float | None,
        eccentricity: float | None,
        inclination: float | None,
        periapsis: float | None,
        ascending_node: float | None,
        mean_anomaly: float | None,
        orbital_period: float | None,
        timestamp: str,
    ) -> None:
        if semi_major_axis is None or orbital_period is None or orbital_period <= 0:
            return

        with self._lock:
            record = OrbitalBodyRecord(
                body_id=body_id,
                body_name=body_name,
                semi_major_axis_m=float(semi_major_axis),
                eccentricity=float(eccentricity or 0.0),
                orbital_inclination_deg=float(inclination or 0.0),
                periapsis_deg=float(periapsis or 0.0),
                ascending_node_deg=float(ascending_node or 0.0),
                mean_anomaly_deg=float(mean_anomaly or 0.0),
                orbital_period_s=float(orbital_period),
                epoch_timestamp=timestamp,
            )
            self._bodies[body_id] = record

        # Propagate current position and dispatch event
        pos = self.get_body_position(body_id)
        if pos:
            dist = math.sqrt(pos.x**2 + pos.y**2 + pos.z**2)
            ev = BodyPositionPropagated(
                body_id=body_id,
                body_name=body_name,
                x_ls=pos.x,
                y_ls=pos.y,
                z_ls=pos.z,
                distance_from_barycenter_ls=round(dist, 3),
            )
            self._dispatcher.dispatch(ev)

    def attach(self) -> None:
        """Subscribes to ScanPlanet, ScanStar, and FSDJump events."""
        if self._attached:
            return

        def _on_scan_planet(event: ScanPlanet) -> None:
            self._record_body(
                body_id=getattr(event, "BodyID", 0),
                body_name=getattr(event, "BodyName", "Unknown Planet"),
                semi_major_axis=getattr(event, "SemiMajorAxis", None),
                eccentricity=getattr(event, "Eccentricity", None),
                inclination=getattr(event, "OrbitalInclination", None),
                periapsis=getattr(event, "Periapsis", None),
                ascending_node=getattr(event, "AscendingNode", None),
                mean_anomaly=getattr(event, "MeanAnomaly", None),
                orbital_period=getattr(event, "OrbitalPeriod", None),
                timestamp=getattr(event, "timestamp", datetime.now(UTC).isoformat()),
            )

        def _on_scan_star(event: ScanStar) -> None:
            self._record_body(
                body_id=getattr(event, "BodyID", 0),
                body_name=getattr(event, "BodyName", "Unknown Star"),
                semi_major_axis=getattr(event, "SemiMajorAxis", None),
                eccentricity=getattr(event, "Eccentricity", None),
                inclination=getattr(event, "OrbitalInclination", None),
                periapsis=getattr(event, "Periapsis", None),
                ascending_node=getattr(event, "AscendingNode", None),
                mean_anomaly=getattr(event, "MeanAnomaly", None),
                orbital_period=getattr(event, "OrbitalPeriod", None),
                timestamp=getattr(event, "timestamp", datetime.now(UTC).isoformat()),
            )

        def _on_jump(event: FSDJump) -> None:
            with self._lock:
                self._bodies.clear()

        sub_planet = self._dispatcher.subscribe(ScanPlanet, _on_scan_planet)
        sub_star = self._dispatcher.subscribe(ScanStar, _on_scan_star)
        sub_jump = self._dispatcher.subscribe(FSDJump, _on_jump)

        self._subscriptions.extend([sub_planet, sub_star, sub_jump])
        self._attached = True

    def detach(self) -> None:
        """Unsubscribes from the event bus."""
        for sub in self._subscriptions:
            self._dispatcher.unsubscribe(sub)
        self._subscriptions.clear()
        self._attached = False
