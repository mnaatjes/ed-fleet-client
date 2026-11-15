"""Use case for querying orbital and flight metrics from domain services (UC-04)."""

from __future__ import annotations

from typing import Any

from ed_fleet_client.core.domain.services.orbital import OrbitalMechanicsService


class GetOrbitalMetricsUseCase:
    """Provides access to orbital mechanics calculations (UC-04)."""

    def __init__(self, orbital_service: OrbitalMechanicsService) -> None:
        self._orbital_service = orbital_service

    def list_tracked_bodies(self) -> list[dict[str, Any]]:
        """Returns all tracked orbital bodies from the orbital service."""
        return self._orbital_service.list_bodies()

    def get_periapsis_apoapsis_ls(self, body_id: int) -> tuple[float, float] | None:
        """Returns (periapsis, apoapsis) in light-seconds for a tracked body."""
        return self._orbital_service.get_periapsis_apoapsis_ls(body_id)
