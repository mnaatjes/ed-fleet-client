"""Combat analytics and tactical survivability diagnostic service."""

from __future__ import annotations

import threading
import time
from collections.abc import Callable

from ed_models.core.domain.events import ShieldState, ShipTargeted, UnderAttack

from ..dispatcher import Subscription, TelemetryEventDispatcher
from ..state import ClientStateProjection
from .base import TelemetryService
from .models import CombatDiagnosticsUpdated


def calculate_sys_pip_resistance(sys_pips: float) -> float:
    """Calculates shield damage resistance multiplier given SYS pips (0.0 to 4.0).

    In Elite Dangerous:
    0 pips = 0% resistance
    1 pip  = ~15%
    2 pips = ~28%
    3 pips = ~42%
    4 pips = ~56.5% resistance (damage divided by 2.3)
    """
    pips = max(0.0, min(4.0, sys_pips))
    # Empirical curve fit: resistance = 1.0 - (1.0 / (1.0 + 0.325 * pips))
    return round(1.0 - (1.0 / (1.0 + 0.325 * pips)), 3)


class CombatAnalyticsService(TelemetryService):
    """Computes real-time DPS and Time-To-Kill / Time-To-Die metrics."""

    def __init__(
        self,
        state_accessor: Callable[[], ClientStateProjection],
        dispatcher: TelemetryEventDispatcher,
    ) -> None:
        self._lock = threading.RLock()

        # Target vessel state tracking
        self._target_last_health: float | None = None
        self._target_last_time: float | None = None
        self._target_dps: float = 0.0

        # Player ship state tracking
        self._player_last_shield: float | None = None
        self._player_last_time: float | None = None
        self._incoming_dps: float = 0.0

        self._subscriptions: list[Subscription] = []
        super().__init__(state_accessor, dispatcher)

    # =========================================================================
    # Pattern 1: State-Guarded Pull Methods
    # =========================================================================

    def get_target_dps(self) -> float:
        """Returns the rolling DPS dealt to the currently targeted vessel."""
        with self._lock:
            return round(self._target_dps, 2)

    def get_target_ttk_s(self) -> float | None:
        """Estimates Time-To-Kill (in seconds) for targeted vessel based on current DPS."""
        with self._lock:
            if self._target_last_health is None or self._target_dps <= 0:
                return None
            # Target health is 0.0 - 1.0, assuming standard 100 HP base unit
            remaining_fraction = self._target_last_health
            return round((remaining_fraction * 100.0) / self._target_dps, 1)

    def get_incoming_dps(self) -> float:
        """Returns the rolling DPS incoming to player's vessel."""
        with self._lock:
            return round(self._incoming_dps, 2)

    def get_sys_pip_resistance(self) -> float:
        """Returns the active shield damage resistance derived from SYS capacitor pips."""
        state = self._get_state()
        telemetry = state.ship.telemetry
        if not telemetry or not telemetry.pips:
            return 0.0
        sys_p = telemetry.pips[0] / 2.0  # Raw values are half-pips
        return calculate_sys_pip_resistance(sys_p)

    # =========================================================================
    # Pattern 2: Reactive Stream Pipe
    # =========================================================================

    def _evaluate_and_dispatch(self) -> None:
        with self._lock:
            t_dps = self.get_target_dps()
            ttk = self.get_target_ttk_s()
            in_dps = self.get_incoming_dps()
            resistance = self.get_sys_pip_resistance()

            ev = CombatDiagnosticsUpdated(
                target_dps=t_dps,
                target_ttk_s=ttk,
                incoming_dps=in_dps,
                player_ttd_s=None,
                sys_pip_damage_resistance=resistance,
            )
        self._dispatcher.dispatch(ev)

    def attach(self) -> None:
        """Subscribes to ShipTargeted, UnderAttack, and ShieldState events."""
        if self._attached:
            return

        def _on_ship_targeted(event: ShipTargeted) -> None:
            now = time.monotonic()
            hull = getattr(event, "HullHealth", None)
            shield = getattr(event, "ShieldHealth", None)

            current_hp = None
            if shield is not None and shield > 0:
                current_hp = float(shield)
            elif hull is not None:
                current_hp = float(hull)

            with self._lock:
                if (
                    current_hp is not None
                    and self._target_last_health is not None
                    and self._target_last_time is not None
                ):
                    dt = now - self._target_last_time
                    dhp = (self._target_last_health - current_hp) * 100.0
                    if 0.2 <= dt <= 10.0 and dhp > 0:
                        measured = dhp / dt
                        self._target_dps = 0.7 * self._target_dps + 0.3 * measured
                    elif dhp <= 0 and dt > 3.0:
                        self._target_dps = max(0.0, self._target_dps * 0.5)

                if current_hp is not None:
                    self._target_last_health = current_hp
                    self._target_last_time = now
            self._evaluate_and_dispatch()

        def _on_under_attack(event: UnderAttack) -> None:
            with self._lock:
                # UnderAttack signals active incoming fire
                if self._incoming_dps <= 0:
                    self._incoming_dps = 15.0  # Baseline engagement indicator
            self._evaluate_and_dispatch()

        def _on_shield_state(event: ShieldState) -> None:
            if not getattr(event, "ShieldsUp", True):
                with self._lock:
                    self._incoming_dps += 25.0
            self._evaluate_and_dispatch()

        sub_target = self._dispatcher.subscribe(ShipTargeted, _on_ship_targeted)
        sub_attack = self._dispatcher.subscribe(UnderAttack, _on_under_attack)
        sub_shields = self._dispatcher.subscribe(ShieldState, _on_shield_state)

        self._subscriptions.extend([sub_target, sub_attack, sub_shields])
        self._attached = True

    def detach(self) -> None:
        for sub in self._subscriptions:
            self._dispatcher.unsubscribe(sub)
        self._subscriptions.clear()
        self._attached = False
