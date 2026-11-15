---
title: "ADR 0004: End-User Control Plane Facade Architecture & UX"
status: "proposed"
date: "2026-11-15"
tags: ["architecture", "adr", "facade", "ux", "diataxis", "ed-fleet-client"]
---

# ADR 0004: End-User Control Plane Facade Architecture & UX

## 1. Context and Verification

### 1.1 Verification of Migrated Core Capabilities

Before finalizing the end-user control plane (`EliteDangerousClient` in `src/ed_fleet_client/adapters/driving/facade.py`), we verified that all event-listener and reducer-state capabilities from `ed-integration-smoke` are present in `core/domain/`:
* **Event Listeners & Triggers:** `TelemetryEventDispatcher` (`core/domain/dispatcher/dispatcher.py`) provides `@dispatcher.on(event_type)`, `subscribe()`, `unsubscribe()`, `clear()`, `dispatch()`, and `dispatch_async()` for all `ed_models` telemetry events.
* **High-Frequency Reducer States:** `TelemetryStateEngine` and `ClientStateProjection` (`core/domain/state/`) maintain immutable projections for `location` (`LocationProjection`), `session` (`SessionProjection`), and `ship` (`ShipProjection`), guarded by `validate_mutex_invariants()`.

### 1.2 Problem Statement

Currently, `EliteDangerousClient` exposes `state`, `dispatcher`, `orbital`, `navigation`, `astrophysics`, `flight_performance`, `combat_analytics`, `get_snapshot()`, `connect()`, and `disconnect()`. However, end users still have to reach through `client.dispatcher.on(...)` or `client.state.location` rather than having a cohesive, ergonomic control plane.

---

## 2. Decision Outcome

We standardize `EliteDangerousClient` (`src/ed_fleet_client/adapters/driving/facade.py`) as the **single, ergonomic end-user control plane** with the following UX-first API surface:

### 2.1 Lifecycle & Connection Control
* `async def connect() -> None`: Starts the telemetry stream (`StreamIngestionPort.start()`).
* `async def disconnect() -> None`: Stops the telemetry stream (`StreamIngestionPort.stop()`).
* `async def __aenter__() -> EliteDangerousClient` / `async def __aexit__(...) -> None`: Supports `async with create_client() as client:` for automatic connection/disconnection.

### 2.2 Event Listeners & Triggers (Delegated to `TelemetryEventDispatcher`)
* `def on(event_type: type[E]) -> Callable[[EventHandler], EventHandler]`: Decorator (`@client.on(FSDJump)`) for registering sync or async handlers.
* `def subscribe(event_type: type[E], handler: EventHandler) -> Subscription`: Programmatic subscription returning a `Subscription` token.
* `def unsubscribe(subscription: Subscription) -> bool`: Removes an active subscription.

### 2.3 High-Frequency State Projections (Delegated to `TelemetryStateEngine`)
* `state -> ClientStateProjection`: Full immutable state snapshot.
* `location -> LocationProjection`: Current star system, station, body, and coordinates.
* `session -> SessionProjection`: Current commander, game mode, and active session status.
* `ship -> ShipProjection`: Current ship, fuel, cargo, pips, and flight flags.

### 2.4 Companion Snapshots & Domain Services
* `async def get_snapshot(name: str, endpoint: str) -> Any`: Fetches and hydrates companion snapshots (`UC-03`).
* `orbital -> GetOrbitalMetricsUseCase`: Orbital mechanics queries (`UC-04`).
* `navigation -> NavigationService`: Jump route and waypoint tracking.
* `astrophysics -> AstrophysicsService`: Stellar/planetary scan analytics.
* `flight_performance -> FlightPerformanceService`: Fuel and flight efficiency metrics.
* `combat_analytics -> CombatAnalyticsService`: Combat and bounty analytics.

---

## 3. Testing Procedures

1. **Facade Unit & Integration Tests (`tests/integration/test_client_facade.py`):**
   * Verify `create_client()` wires all ports, use cases, and 5 domain services.
   * Verify `@client.on(...)`, `subscribe()`, `unsubscribe()`, `location`, `session`, `ship`, and `async with create_client()` using `InMemoryTelemetryTransportPort`.
2. **Deterministic Quality Gate (`scripts/verify.py`):**
   * Pre-commit (`ruff`, `ruff-format`), ImportLinter (5/5 contracts), MyPy (`src/`, `tests/`), and Pytest (`tests/`).

---

## 4. Diataxis Documentation Plan

Implementation of this ADR must include living user-facing documentation under `docs/` following the Diataxis framework:
* **`docs/reference/client_facade.md`:** Complete API reference for `EliteDangerousClient`, `create_client()`, state projections (`ClientStateProjection`, `LocationProjection`, `SessionProjection`, `ShipProjection`), and domain service properties.
* **`docs/how-to/subscribe_to_telemetry_events.md`:** Step-by-step guide for connecting with `async with create_client()`, registering `@client.on(...)` listeners, reading `client.ship` / `client.location`, and fetching companion snapshots.
