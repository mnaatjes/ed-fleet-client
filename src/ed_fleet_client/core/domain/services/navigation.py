"""Navigation calculation engine and reactive stream deriver."""

from __future__ import annotations

import math
import threading
from collections.abc import Callable
from typing import Any

from ed_models import StatusTelemetry
from ed_models.core.domain.events import ApproachSettlement, FSDJump, FSDTarget, ShipTargeted

from ..dispatcher import Subscription, TelemetryEventDispatcher
from ..state import ClientStateProjection
from .base import TelemetryService
from .models import (
    NavBearingUpdated,
    NavDistanceUpdated,
    RouteProgressUpdated,
    TargetLockedUpdated,
)


def calculate_great_circle_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates initial great-circle bearing (degrees 0.0 to 360.0) from point 1 to point 2."""
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_lambda = math.radians(lon2 - lon1)

    y = math.sin(delta_lambda) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(delta_lambda)

    theta = math.atan2(y, x)
    bearing = (math.degrees(theta) + 360.0) % 360.0
    return round(bearing, 2)


def calculate_surface_distance_km(
    lat1: float, lon1: float, lat2: float, lon2: float, radius_km: float = 6371.0
) -> float:
    """Calculates great-circle distance in kilometers using the Haversine formula."""
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(radius_km * c, 2)


class NavigationService(TelemetryService):
    """Provides geodetic navigation calculations, entity targeting, and route tracking."""

    def __init__(
        self,
        state_accessor: Callable[[], ClientStateProjection],
        dispatcher: TelemetryEventDispatcher,
    ) -> None:
        self._lock = threading.RLock()
        # Surface waypoint target
        self._target_name: str | None = None
        self._target_lat: float | None = None
        self._target_lon: float | None = None
        self._target_radius_km: float = 6371.0

        # General destination (station, celestial body, star system) from Status.Destination
        self._destination_name: str | None = None
        self._destination_system_address: int | None = None
        self._destination_body_id: int | None = None

        # Vessel / entity target from ShipTargeted
        self._target_locked: bool = False
        self._target_ship_model: str = ""
        self._target_pilot_name: str = ""
        self._target_shield_health: float | None = None
        self._target_hull_health: float | None = None
        self._target_legal_status: str = ""

        # Hyperspace Route from FSDTarget
        self._fsd_target_system: str | None = None
        self._fsd_star_class: str = ""
        self._fsd_remaining_jumps: int = 0

        self._subscriptions: list[Subscription] = []
        super().__init__(state_accessor, dispatcher)

    # =========================================================================
    # Pattern 1: State-Guarded Pull Methods
    # =========================================================================

    def get_destination(self) -> tuple[str, float, float] | None:
        """Returns the current destination (name, latitude, longitude) or None if unset."""
        with self._lock:
            if self._target_name and self._target_lat is not None and self._target_lon is not None:
                return (self._target_name, self._target_lat, self._target_lon)
            return None

    def set_destination(
        self, name: str, latitude: float, longitude: float, planet_radius_km: float = 6371.0
    ) -> None:
        """Manually sets a navigation destination waypoint."""
        with self._lock:
            self._target_name = name
            self._target_lat = latitude
            self._target_lon = longitude
            self._target_radius_km = planet_radius_km
            self._evaluate_and_dispatch()

    def clear_destination(self) -> None:
        """Clears the active navigation target."""
        with self._lock:
            self._target_name = None
            self._target_lat = None
            self._target_lon = None

    @property
    def target_name(self) -> str | None:
        """Returns the currently targeted destination settlement name, if set."""
        with self._lock:
            return self._target_name

    @property
    def destination_name(self) -> str | None:
        """Returns the active locked destination name from cockpit Status telemetry."""
        with self._lock:
            return self._destination_name

    @property
    def locked_ship(self) -> dict[str, Any] | None:
        """Returns locked vessel attributes or None if no vessel is targeted."""
        with self._lock:
            if not self._target_locked or not self._target_ship_model:
                return None
            return {
                "locked": self._target_locked,
                "ship_model": self._target_ship_model,
                "pilot_name": self._target_pilot_name,
                "shield_health": self._target_shield_health,
                "hull_health": self._target_hull_health,
                "legal_status": self._target_legal_status,
            }

    @property
    def hyperspace_route(self) -> dict[str, Any] | None:
        """Returns active hyperspace jump route progress or None if unrouted."""
        with self._lock:
            if not self._fsd_target_system:
                return None
            return {
                "destination_system": self._fsd_target_system,
                "star_class": self._fsd_star_class,
                "remaining_jumps": self._fsd_remaining_jumps,
            }

    def bearing_to_target(self) -> float | None:
        """Calculates initial great-circle bearing to destination, or None if inputs unavailable."""
        with self._lock:
            if self._target_lat is None or self._target_lon is None:
                return None

            state = self._get_state()
            telemetry = state.ship.telemetry
            if not telemetry or telemetry.latitude is None or telemetry.longitude is None:
                return None

            return calculate_great_circle_bearing(
                telemetry.latitude,
                telemetry.longitude,
                self._target_lat,
                self._target_lon,
            )

    def distance_to_target_km(self) -> float | None:
        """Calculates surface distance in kilometers to destination, or None if unavailable."""
        with self._lock:
            if self._target_lat is None or self._target_lon is None:
                return None

            state = self._get_state()
            telemetry = state.ship.telemetry
            if not telemetry or telemetry.latitude is None or telemetry.longitude is None:
                return None

            radius_km = (
                telemetry.planet_radius / 1000.0
                if telemetry.planet_radius
                else self._target_radius_km
            )
            return calculate_surface_distance_km(
                telemetry.latitude,
                telemetry.longitude,
                self._target_lat,
                self._target_lon,
                radius_km=radius_km,
            )

    # =========================================================================
    # Pattern 2: Reactive Stream Pipe
    # =========================================================================

    def _evaluate_and_dispatch(self) -> None:
        """Internal evaluator that dispatches derived events once all parameters are valid."""
        with self._lock:
            if self._target_lat is None or self._target_lon is None or not self._target_name:
                return

            state = self._get_state()
            telemetry = state.ship.telemetry
            if not telemetry or telemetry.latitude is None or telemetry.longitude is None:
                return

            radius_km = (
                telemetry.planet_radius / 1000.0
                if telemetry.planet_radius
                else self._target_radius_km
            )
            bearing = calculate_great_circle_bearing(
                telemetry.latitude,
                telemetry.longitude,
                self._target_lat,
                self._target_lon,
            )
            distance = calculate_surface_distance_km(
                telemetry.latitude,
                telemetry.longitude,
                self._target_lat,
                self._target_lon,
                radius_km=radius_km,
            )

            heading = telemetry.heading
            deflection = (
                ((bearing - heading + 180.0) % 360.0) - 180.0 if heading is not None else None
            )

            # Dispatch derived events onto the client's event bus
            bearing_ev = NavBearingUpdated(
                destination_name=self._target_name,
                bearing_deg=bearing,
                distance_km=distance,
                heading_deg=heading,
                deflection_deg=round(deflection, 2) if deflection is not None else None,
            )
            self._dispatcher.dispatch(bearing_ev)

            distance_ev = NavDistanceUpdated(
                destination_name=self._target_name,
                distance_km=distance,
                altitude_m=telemetry.altitude,
            )
            self._dispatcher.dispatch(distance_ev)

    def attach(self) -> None:
        """Subscribes to StatusTelemetry and journal events to drive derivations."""
        if self._attached:
            return

        def _on_status(event: StatusTelemetry) -> None:
            dest = event.additional_fields.get("Destination")
            if isinstance(dest, dict):
                with self._lock:
                    self._destination_name = dest.get("Name")
                    self._destination_system_address = dest.get("System")
                    self._destination_body_id = dest.get("Body")
            self._evaluate_and_dispatch()

        def _on_settlement(event: ApproachSettlement) -> None:
            lat = getattr(event, "Latitude", None)
            lon = getattr(event, "Longitude", None)
            name = getattr(event, "Name", "Surface Settlement")
            if lat is not None and lon is not None:
                with self._lock:
                    self._target_name = name
                    self._target_lat = float(lat)
                    self._target_lon = float(lon)
                    self._evaluate_and_dispatch()

        def _on_ship_targeted(event: ShipTargeted) -> None:
            locked = bool(getattr(event, "TargetLocked", False))
            with self._lock:
                self._target_locked = locked
                if locked:
                    self._target_ship_model = getattr(event, "Ship_Localised", "") or getattr(
                        event, "Ship", ""
                    )
                    self._target_pilot_name = getattr(event, "PilotName_Localised", "") or getattr(
                        event, "PilotName", ""
                    )
                    self._target_shield_health = getattr(event, "ShieldHealth", None)
                    self._target_hull_health = getattr(event, "HullHealth", None)
                    self._target_legal_status = getattr(event, "LegalStatus", "")
                else:
                    self._target_ship_model = ""
                    self._target_pilot_name = ""
                    self._target_shield_health = None
                    self._target_hull_health = None
                    self._target_legal_status = ""

                target_ev = TargetLockedUpdated(
                    locked=locked,
                    target_type="Ship" if locked else "None",
                    target_name=self._target_ship_model,
                    pilot_name=self._target_pilot_name,
                    ship_model=self._target_ship_model,
                    shield_health=self._target_shield_health,
                    hull_health=self._target_hull_health,
                    legal_status=self._target_legal_status,
                )
            self._dispatcher.dispatch(target_ev)

        def _on_fsd_target(event: FSDTarget) -> None:
            system_name = getattr(event, "Name", "")
            remaining = int(getattr(event, "RemainingJumpsInRoute", 1))
            star_class = getattr(event, "StarClass", "")
            with self._lock:
                self._fsd_target_system = system_name
                self._fsd_remaining_jumps = remaining
                self._fsd_star_class = star_class
                route_ev = RouteProgressUpdated(
                    destination_system=system_name,
                    star_class=star_class,
                    remaining_jumps=remaining,
                )
            self._dispatcher.dispatch(route_ev)

        def _on_fsd_jump(event: FSDJump) -> None:
            with self._lock:
                if self._fsd_remaining_jumps > 0:
                    self._fsd_remaining_jumps -= 1
                    if self._fsd_remaining_jumps == 0:
                        self._fsd_target_system = None
                self.clear_destination()

        sub_status = self._dispatcher.subscribe(StatusTelemetry, _on_status)
        sub_settlement = self._dispatcher.subscribe(ApproachSettlement, _on_settlement)
        sub_ship_targeted = self._dispatcher.subscribe(ShipTargeted, _on_ship_targeted)
        sub_fsd_target = self._dispatcher.subscribe(FSDTarget, _on_fsd_target)
        sub_fsd_jump = self._dispatcher.subscribe(FSDJump, _on_fsd_jump)

        self._subscriptions.extend(
            [sub_status, sub_settlement, sub_ship_targeted, sub_fsd_target, sub_fsd_jump]
        )
        self._attached = True

    def detach(self) -> None:
        """Unsubscribes from the event bus."""
        for sub in self._subscriptions:
            self._dispatcher.unsubscribe(sub)
        self._subscriptions.clear()
        self._attached = False
