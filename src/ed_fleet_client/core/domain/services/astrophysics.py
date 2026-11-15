"""Astrophysics and stellar classification service."""

from __future__ import annotations

import math
import threading
from collections.abc import Callable

from ed_models.core.domain.events.exploration.scan import ScanPlanet, ScanStar

from ..dispatcher import Subscription, TelemetryEventDispatcher
from ..state import ClientStateProjection
from .base import TelemetryService
from .models import HabitableZoneEvaluated

# Constants
SOLAR_RADIUS_M = 696_340_000.0
SOLAR_TEMPERATURE_K = 5778.0
AU_METERS = 149_597_870_700.0
SPEED_OF_LIGHT_M_S = 299_792_458.0


def calculate_stellar_luminosity_solar(radius_m: float, surface_temp_k: float) -> float:
    """Calculates star luminosity relative to the Sun (L / L_sun) via Stefan-Boltzmann Law."""
    r_ratio = radius_m / SOLAR_RADIUS_M
    t_ratio = surface_temp_k / SOLAR_TEMPERATURE_K
    return round((r_ratio**2) * (t_ratio**4), 4)


def calculate_habitable_zone_au(luminosity_solar: float) -> tuple[float, float]:
    """Calculates inner and outer habitable zone boundaries in AU."""
    l_sol = max(1e-6, luminosity_solar)
    inner_au = math.sqrt(l_sol / 1.1)
    outer_au = math.sqrt(l_sol / 0.53)
    return (round(inner_au, 4), round(outer_au, 4))


class AstrophysicsService(TelemetryService):
    """Computes stellar luminosity, habitable zones, and planetary equilibrium classification."""

    def __init__(
        self,
        state_accessor: Callable[[], ClientStateProjection],
        dispatcher: TelemetryEventDispatcher,
    ) -> None:
        self._lock = threading.RLock()
        self._primary_star_name: str = ""
        self._primary_star_luminosity: float = 1.0
        self._habitable_inner_au: float = 0.95
        self._habitable_outer_au: float = 1.37

        self._subscriptions: list[Subscription] = []
        super().__init__(state_accessor, dispatcher)

    # =========================================================================
    # Pattern 1: State-Guarded Pull Methods
    # =========================================================================

    def get_habitable_zone_au(self) -> tuple[float, float]:
        """Returns the current system's habitable zone boundaries (inner, outer) in AU."""
        with self._lock:
            return (self._habitable_inner_au, self._habitable_outer_au)

    def get_habitable_zone_ls(self) -> tuple[float, float]:
        """Returns the current system's habitable zone boundaries in light-seconds (LS)."""
        with self._lock:
            inner_ls = (self._habitable_inner_au * AU_METERS) / SPEED_OF_LIGHT_M_S
            outer_ls = (self._habitable_outer_au * AU_METERS) / SPEED_OF_LIGHT_M_S
            return (round(inner_ls, 1), round(outer_ls, 1))

    def is_in_habitable_zone(self, distance_au: float) -> bool:
        """Determines whether a given orbital distance falls within the liquid-water zone."""
        with self._lock:
            return self._habitable_inner_au <= distance_au <= self._habitable_outer_au

    # =========================================================================
    # Pattern 2: Reactive Stream Pipe
    # =========================================================================

    def attach(self) -> None:
        """Subscribes to ScanStar and ScanPlanet events."""
        if self._attached:
            return

        def _on_scan_star(event: ScanStar) -> None:
            radius = getattr(event, "Radius", None)
            temp = getattr(event, "SurfaceTemperature", None)
            name = getattr(event, "BodyName", "Primary Star")

            if radius and temp:
                lum = calculate_stellar_luminosity_solar(float(radius), float(temp))
                inner_au, outer_au = calculate_habitable_zone_au(lum)

                with self._lock:
                    self._primary_star_name = name
                    self._primary_star_luminosity = lum
                    self._habitable_inner_au = inner_au
                    self._habitable_outer_au = outer_au

                inner_ls, outer_ls = self.get_habitable_zone_ls()
                ev = HabitableZoneEvaluated(
                    star_name=name,
                    luminosity_solar=lum,
                    habitable_inner_au=inner_au,
                    habitable_outer_au=outer_au,
                    habitable_inner_ls=inner_ls,
                    habitable_outer_ls=outer_ls,
                    in_habitable_zone=False,
                    planet_name=None,
                )
                self._dispatcher.dispatch(ev)

        def _on_scan_planet(event: ScanPlanet) -> None:
            semi_major = getattr(event, "SemiMajorAxis", None)
            name = getattr(event, "BodyName", "Planet")
            if semi_major:
                dist_au = float(semi_major) / AU_METERS
                in_hz = self.is_in_habitable_zone(dist_au)
                inner_ls, outer_ls = self.get_habitable_zone_ls()

                with self._lock:
                    lum = self._primary_star_luminosity
                    inner_au = self._habitable_inner_au
                    outer_au = self._habitable_outer_au

                ev = HabitableZoneEvaluated(
                    star_name=self._primary_star_name,
                    luminosity_solar=lum,
                    habitable_inner_au=inner_au,
                    habitable_outer_au=outer_au,
                    habitable_inner_ls=inner_ls,
                    habitable_outer_ls=outer_ls,
                    in_habitable_zone=in_hz,
                    planet_name=name,
                )
                self._dispatcher.dispatch(ev)

        sub_star = self._dispatcher.subscribe(ScanStar, _on_scan_star)
        sub_planet = self._dispatcher.subscribe(ScanPlanet, _on_scan_planet)

        self._subscriptions.extend([sub_star, sub_planet])
        self._attached = True

    def detach(self) -> None:
        for sub in self._subscriptions:
            self._dispatcher.unsubscribe(sub)
        self._subscriptions.clear()
        self._attached = False
