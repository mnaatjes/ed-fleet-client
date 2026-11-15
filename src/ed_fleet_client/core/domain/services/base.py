"""Base contracts and lifecycle enforcement for telemetry domain services."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable

from ..dispatcher import TelemetryEventDispatcher
from ..state import ClientStateProjection


class TelemetryService(ABC):
    """Abstract base class establishing the contract for all telemetry domain services.

    Enforces that services accept a state accessor (Pattern 1) and a dispatcher (Pattern 2)
    and provide lifecycle attachment/detachment.
    """

    def __init__(
        self,
        state_accessor: Callable[[], ClientStateProjection],
        dispatcher: TelemetryEventDispatcher,
    ) -> None:
        self._get_state = state_accessor
        self._dispatcher = dispatcher
        self._attached = False
        self.attach()

    @property
    def is_attached(self) -> bool:
        """Indicates if the service is actively listening to the event dispatcher."""
        return self._attached

    @abstractmethod
    def attach(self) -> None:
        """Binds internal event listeners to the dispatcher (Pattern 2)."""

    @abstractmethod
    def detach(self) -> None:
        """Removes internal event listeners from the dispatcher."""
