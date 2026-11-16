"""Public package exports for ed-fleet-client."""

from __future__ import annotations

from ed_fleet_client.adapters.driving.facade import EliteDangerousClient
from ed_fleet_client.adapters.driving.stream.models import StreamMonitorConfig
from ed_fleet_client.bootstrap.container import create_client

__all__ = (
    "EliteDangerousClient",
    "StreamMonitorConfig",
    "create_client",
)
