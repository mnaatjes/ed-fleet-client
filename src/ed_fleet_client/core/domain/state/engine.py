"""Coordinates event reduction into a thread-safe materialized client state projection
with pre-reduction Mutex Invariant validation gates.
"""

from __future__ import annotations

import logging
import threading

from ed_models import JournalEvent, StatusTelemetry

from .models import (
    ClientStateProjection,
    LocationProjection,
    SessionProjection,
    ShipProjection,
)
from .reducers import reduce_client_state

logger = logging.getLogger(__name__)


def validate_mutex_invariants(telemetry: StatusTelemetry) -> bool:
    """Verifies that an incoming StatusTelemetry frame satisfies physical mutual exclusion rules.

    Invariants Enforced (ADR 0014 / Research 0001):
    1. Spatial Flight Regimes:
       A vessel cannot be simultaneously DOCKED and in SUPERCRUISE or LANDED.
    2. Cockpit Hardware Interlocks:
       Supercruise cannot assert LANDING_GEAR_DOWN or CARGO_SCOOP_DEPLOYED.
    """
    flags = getattr(telemetry, "Flags", 0)
    if isinstance(flags, int):
        docked = bool(flags & (1 << 0))
        landed = bool(flags & (1 << 1))
        gear = bool(flags & (1 << 2))
        supercruise = bool(flags & (1 << 4))
        scoop = bool(flags & (1 << 9))

        # Spatial Mutex Rule
        if docked and supercruise:
            logger.warning("Mutex Violation: Status claims DOCKED and SUPERCRUISE simultaneously.")
            return False
        if landed and supercruise:
            logger.warning("Mutex Violation: Status claims LANDED and SUPERCRUISE simultaneously.")
            return False

        # Hardware Interlock Rule
        if supercruise and (gear or scoop):
            logger.warning(
                "Mutex Violation: Status claims SUPERCRUISE with landing gear or scoop deployed."
            )
            return False

    return True


class TelemetryStateEngine:
    """Coordinates event reduction into a thread-safe materialized client state projection."""

    def __init__(self, initial_state: ClientStateProjection | None = None) -> None:
        self._lock = threading.RLock()
        self._state = initial_state or ClientStateProjection()
        self._corrupt_frame_count: int = 0

    @property
    def current(self) -> ClientStateProjection:
        """Returns the current immutable materialized state snapshot."""
        with self._lock:
            return self._state

    @property
    def corrupt_frame_count(self) -> int:
        """Total number of rejected malformed/mutex-violating frames."""
        with self._lock:
            return self._corrupt_frame_count

    @property
    def location(self) -> LocationProjection:
        """Convenience property for current location projection."""
        with self._lock:
            return self._state.location

    @property
    def session(self) -> SessionProjection:
        """Convenience property for current session projection."""
        with self._lock:
            return self._state.session

    @property
    def ship(self) -> ShipProjection:
        """Convenience property for current ship projection."""
        with self._lock:
            return self._state.ship

    def apply(self, event: JournalEvent | StatusTelemetry) -> ClientStateProjection:
        """Applies an incoming hydrated event or status telemetry and returns the updated state.

        Status frames are passed through the Mutex Invariant Gate before applying.
        """
        with self._lock:
            if isinstance(event, StatusTelemetry) and not validate_mutex_invariants(event):
                self._corrupt_frame_count += 1
                return self._state

            self._state = reduce_client_state(self._state, event)
            return self._state

    def reset(self, new_state: ClientStateProjection | None = None) -> ClientStateProjection:
        """Resets the state engine to default or specified initial state."""
        with self._lock:
            self._state = new_state or ClientStateProjection()
            self._corrupt_frame_count = 0
            return self._state

    def __repr__(self) -> str:
        with self._lock:
            return (
                f"TelemetryStateEngine(seq={self._state.sequence_number}, "
                f"system='{self._state.location.star_system}', "
                f"commander='{self._state.session.commander_name}')"
            )
