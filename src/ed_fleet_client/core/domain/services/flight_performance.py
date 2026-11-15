"""Flight performance and propulsion dynamics calculation service."""

from __future__ import annotations

import threading
import time
from collections.abc import Callable

from ed_models import StatusTelemetry
from ed_models.core.domain.events import FSDJump, Loadout

from ..dispatcher import Subscription, TelemetryEventDispatcher
from ..state import ClientStateProjection
from .base import TelemetryService
from .models import PerformanceMetricsUpdated


class FlightPerformanceService(TelemetryService):
    """Computes live ship mass, dynamic jump reach, and fuel burn rates."""

    def __init__(
        self,
        state_accessor: Callable[[], ClientStateProjection],
        dispatcher: TelemetryEventDispatcher,
    ) -> None:
        self._lock = threading.RLock()
        self._unladen_mass: float = 0.0
        self._cargo_capacity: int = 0
        self._max_unladen_jump_range: float = 0.0

        # Fuel burn tracking
        self._last_fuel: float | None = None
        self._last_fuel_time: float | None = None
        self._burn_rate_t_per_hr: float = 0.0

        self._subscriptions: list[Subscription] = []
        super().__init__(state_accessor, dispatcher)

    # =========================================================================
    # Pattern 1: State-Guarded Pull Methods
    # =========================================================================

    def get_total_mass_t(self) -> float:
        """Returns instantaneous total ship mass (unladen + cargo + fuel)."""
        with self._lock:
            state = self._get_state()
            ship = state.ship
            telemetry = ship.telemetry

            cargo_t = float(telemetry.cargo) if telemetry else 0.0
            fuel_t = float(telemetry.fuel_main + telemetry.fuel_reservoir) if telemetry else 0.0
            base_mass = self._unladen_mass if self._unladen_mass > 0 else 100.0
            return round(base_mass + cargo_t + fuel_t, 2)

    def get_max_jump_range_ly(self) -> float:
        """Returns live maximum single jump distance scaled by current total vessel mass."""
        with self._lock:
            if self._max_unladen_jump_range <= 0:
                return 0.0

            total_mass = self.get_total_mass_t()
            base_mass = self._unladen_mass if self._unladen_mass > 0 else 100.0
            # Scaled range: Range = Base_Range * (Base_Mass / Total_Mass)
            scaled_range = self._max_unladen_jump_range * (base_mass / max(base_mass, total_mass))
            return round(scaled_range, 2)

    def get_fuel_burn_rate_t_per_hr(self) -> float:
        """Returns the current measured or estimated fuel consumption in tonnes per hour."""
        with self._lock:
            return round(self._burn_rate_t_per_hr, 3)

    def get_remaining_flight_hours(self) -> float | None:
        """Calculates estimated endurance hours remaining on current main fuel tank."""
        with self._lock:
            state = self._get_state()
            telemetry = state.ship.telemetry
            if not telemetry or telemetry.fuel_main <= 0 or self._burn_rate_t_per_hr <= 0:
                return None
            return float(round(float(telemetry.fuel_main) / self._burn_rate_t_per_hr, 2))

    # =========================================================================
    # Pattern 2: Reactive Stream Pipe
    # =========================================================================

    def _evaluate_and_dispatch(self) -> None:
        with self._lock:
            total_mass = self.get_total_mass_t()
            jump_range = self.get_max_jump_range_ly()
            burn_rate = self.get_fuel_burn_rate_t_per_hr()
            remaining_hours = self.get_remaining_flight_hours()

            ev = PerformanceMetricsUpdated(
                total_mass_t=total_mass,
                max_jump_range_ly=jump_range,
                fuel_burn_rate_t_per_hr=burn_rate,
                remaining_flight_hours=remaining_hours,
            )
        self._dispatcher.dispatch(ev)

    def attach(self) -> None:
        """Subscribes to Loadout, FSDJump, and StatusTelemetry."""
        if self._attached:
            return

        def _on_loadout(event: Loadout) -> None:
            with self._lock:
                self._unladen_mass = float(getattr(event, "UnladenMass", 0.0))
                self._cargo_capacity = int(getattr(event, "CargoCapacity", 0))
                self._max_unladen_jump_range = float(getattr(event, "MaxJumpRange", 0.0))
            self._evaluate_and_dispatch()

        def _on_status(event: StatusTelemetry) -> None:
            now = time.monotonic()
            current_fuel = event.fuel_main
            with self._lock:
                if self._last_fuel is not None and self._last_fuel_time is not None:
                    dt = now - self._last_fuel_time
                    dfuel = self._last_fuel - current_fuel
                    if 0.5 <= dt <= 30.0 and 0.0 <= dfuel <= 2.0:
                        measured_rate = (dfuel / dt) * 3600.0
                        # Exponential smoothing
                        self._burn_rate_t_per_hr = (
                            0.8 * self._burn_rate_t_per_hr + 0.2 * measured_rate
                        )
                    elif self._burn_rate_t_per_hr <= 0:
                        # Baseline fallback estimate: ~0.8 tonnes/hr standard cruising
                        self._burn_rate_t_per_hr = 0.8

                self._last_fuel = current_fuel
                self._last_fuel_time = now
            self._evaluate_and_dispatch()

        def _on_jump(event: FSDJump) -> None:
            # Jumping consumes jump fuel; update baseline
            self._evaluate_and_dispatch()

        sub_loadout = self._dispatcher.subscribe(Loadout, _on_loadout)
        sub_status = self._dispatcher.subscribe(StatusTelemetry, _on_status)
        sub_jump = self._dispatcher.subscribe(FSDJump, _on_jump)

        self._subscriptions.extend([sub_loadout, sub_status, sub_jump])
        self._attached = True

    def detach(self) -> None:
        for sub in self._subscriptions:
            self._dispatcher.unsubscribe(sub)
        self._subscriptions.clear()
        self._attached = False
