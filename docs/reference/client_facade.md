---
title: "Reference: EliteDangerousClient Facade"
tags: ["reference", "facade", "api", "state", "services"]
created_at: "2026-11-15"
last_updated_at: "2026-11-15"
---

# Reference: `EliteDangerousClient` Facade

`EliteDangerousClient` (`ed_fleet_client.adapters.driving.facade.EliteDangerousClient`) is the primary end-user control plane, constructed via `ed_fleet_client.create_client()`.

---

## 1. Lifecycle Methods

* `async def connect() -> None`: Starts the telemetry stream ingestion loop.
* `async def disconnect() -> None`: Stops the telemetry stream ingestion loop.
* `async with create_client(config) as client:`: Automatically calls `connect()` on entry and `disconnect()` on exit.

---

## 2. Event Listener Methods

* `on(event_type: type[E])`: Decorator registering a sync or async handler for `event_type`.
* `subscribe(event_type: type[E], handler: EventHandler) -> Subscription`: Programmatically registers a handler and returns a `Subscription` token.
* `unsubscribe(subscription: Subscription) -> bool`: Unregisters an active subscription.

---

## 3. State Projections

* `state -> ClientStateProjection`: Full immutable state snapshot.
* `location -> LocationProjection`: Current star system, station, body, and coordinates.
* `session -> SessionProjection`: Commander name, game mode, and active session status.
* `ship -> ShipProjection`: Ship type, fuel, cargo, pips, and flight flags.

---

## 4. Snapshots & Domain Services

* `async def get_snapshot(name: str, endpoint: str) -> RawSnapshotRecord`: Fetches and hydrates a companion snapshot.
* `orbital -> GetOrbitalMetricsUseCase`: Orbital mechanics queries.
* `navigation -> NavigationService`: Jump route and waypoint tracking.
* `astrophysics -> AstrophysicsService`: Stellar and planetary scan analytics.
* `flight_performance -> FlightPerformanceService`: Fuel and flight efficiency metrics.
* `combat_analytics -> CombatAnalyticsService`: Combat and bounty analytics.
