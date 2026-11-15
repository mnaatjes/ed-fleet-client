"""Public package exports for ed-fleet-client."""

from __future__ import annotations

from .bootstrap.container import create_client
from .client import EliteDangerousClient

__all__ = (
    "EliteDangerousClient",
    "create_client",
)
