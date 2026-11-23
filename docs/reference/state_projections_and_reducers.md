---
title: "State Projections & Reducer Reference"
tags: ["telemetry", "state", "projections", "reducers", "reference", "diataxis"]
created_at: "2026-11-23"
last_updated_at: "2026-11-23"
---

# State Projections & Reducer Reference

> [!NOTE]
> Deterministically generated from **`ed-models` v0.2.1** and `ed_fleet_client.core.domain.state.models` dataclass reflection.

## Overview

`ed-fleet-client` maintains an in-memory, thread-safe reactive state projection through `TelemetryStateEngine`. As telemetry and journal events arrive, pure reducer functions (`reduce_location`, `reduce_session`, `reduce_ship`) fold event payloads into immutable state projections.
Applications read materialized state via top-level accessors on `EliteDangerousClient`:
- `client.location` $\to$ [`LocationProjection`](#1-locationprojection-clientlocation)
- `client.session` $\to$ [`SessionProjection`](#2-sessionprojection-clientsession)
- `client.ship` $\to$ [`ShipProjection`](#3-shipprojection-clientship)
- `client.state` $\to$ [`ClientStateProjection`](#4-clientstateprojection-clientstate)

---

## 1. LocationProjection (`client.location`)

Materialized projection of player spatial location.

| Attribute | Type | Default | Authoritative Source | Description |
| :--- | :--- | :--- | :--- | :--- |
| `star_system` | `str` | `"Unknown"` | `ApproachBody` | Authoritative current star system name. |
| `system_address` | `int | None` | `None` | `ApproachBody` | Unique 64-bit Frontier system address hash. |
| `star_pos` | `tuple[float, float, float]` | `(0.0, 0.0, 0.0)` | *state-internal* | Galactic 3D Cartesian coordinates (x, y, z) in light years. |
| `body` | `str` | `""` | *state-internal* | Current celestial body or star name. |
| `body_id` | `int | None` | `None` | `ApproachBody` | System-unique numerical identifier for current celestial body. |
| `body_type` | `str` | `""` | `FSDJump` | Celestial body classification (e.g. Star, Planet, Station). |
| `station_name` | `str | None` | `None` | `Docked` | Name of the starport, outpost, or carrier currently docked at. |
| `station_type` | `str | None` | `None` | `Docked` | Type of station currently docked at (e.g. Coriolis, Outpost). |
| `market_id` | `int | None` | `None` | `Docked` | Unique 64-bit market identifier for local commodity exchange. |
| `docked` | `bool` | `False` | `CarrierJump` | True if vessel is currently docked at a facility. |
| `in_supercruise` | `bool` | `False` | *state-internal* | True if vessel is currently flying in supercruise regime. |
| `population` | `int` | `0` | `FSDJump` | Total registered population of the current star system. |
| `allegiance` | `str` | `""` | `FSDJump` | Superpower allegiance of the current system (e.g. Federation). |
| `economy` | `str` | `""` | `FSDJump` | Primary economic activity of the current system. |
| `government` | `str` | `""` | `FSDJump` | Government archetype of the current system (e.g. Democracy). |
| `security` | `str` | `""` | `Docked` | System law enforcement security level (e.g. High, Anarchy). |
| `last_updated` | `datetime` | `<computed>` | *state-internal* | UTC timestamp of the last applied state reduction update. |

---

## 2. SessionProjection (`client.session`)

Materialized projection of active commander and game session.

| Attribute | Type | Default | Authoritative Source | Description |
| :--- | :--- | :--- | :--- | :--- |
| `commander_name` | `str` | `"Unknown"` | *state-internal* | Active commander in-game callsign or name. |
| `fid` | `str` | `""` | *state-internal* | Frontier customer account identification hash. |
| `game_mode` | `str` | `""` | *state-internal* | Active game mode (Open, Group, or Solo). |
| `group` | `str` | `""` | `LoadGame` | Private group name if playing in Group mode. |
| `credits` | `int` | `0` | `LoadGame` | Total liquid credit balance available to the commander. |
| `loan` | `int` | `0` | `LoadGame` | Active debt or insurance loan outstanding balance. |
| `is_odyssey` | `bool` | `False` | *state-internal* | True if current game session is running on the Odyssey client. |
| `game_version` | `str` | `""` | *state-internal* | Frontier game build and version release identifier string. |
| `is_alive` | `bool` | `True` | *state-internal* | True if the commander vessel/avatar is currently alive. |
| `last_updated` | `datetime` | `<computed>` | *state-internal* | UTC timestamp of the last applied session state update. |

---

## 3. ShipProjection (`client.ship`)

Materialized projection of ship status and loadout attributes.

| Attribute | Type | Default | Authoritative Source | Description |
| :--- | :--- | :--- | :--- | :--- |
| `ship_type` | `str` | `""` | *state-internal* | Vessel model and chassis identifier (e.g. 'krait_mkii'). |
| `ship_id` | `int | None` | `None` | `FetchRemoteModule` | Commander shipyard instance ID for the active vessel. |
| `ship_name` | `str` | `""` | `LoadGame` | Custom user-given ship name. |
| `ship_ident` | `str` | `""` | `LoadGame` | Custom tail/hull registration callsign (e.g. 'DSV-04'). |
| `hull_value` | `int` | `0` | *state-internal* | Base hull purchase credit valuation. |
| `hull_health` | `float` | `1.0` | `Loadout` | Structural integrity proportion of vessel hull (0.0 to 1.0). |
| `modules_value` | `int` | `0` | *state-internal* | Total credit valuation of all fitted modules and hardpoints. |
| `rebuy` | `int` | `0` | `Loadout` | Total insurance replacement deductible cost. |
| `unladen_mass` | `float` | `0.0` | *state-internal* | Unladen dry hull and module mass in metric tonnes. |
| `cargo_capacity` | `int` | `0` | *state-internal* | Maximum cargo rack capacity in standard metric tonnes. |
| `max_jump_range` | `float` | `0.0` | *state-internal* | Maximum single-jump hyperdrive range in light years. |
| `telemetry` | `StatusTelemetry | None` | `None` | *state-internal* | Latest real-time cockpit StatusTelemetry snapshot frame. |
| `last_updated` | `datetime` | `<computed>` | *state-internal* | UTC timestamp of the last applied ship loadout update. |

---

## 4. ClientStateProjection (`client.state`)

Root immutable materialized state projection for an Elite Dangerous client.

| Attribute | Type | Default | Authoritative Source | Description |
| :--- | :--- | :--- | :--- | :--- |
| `session` | `SessionProjection` | `<computed>` | *state-internal* | Commander and game session projection state. |
| `location` | `LocationProjection` | `<computed>` | `CarrierBuy` | Spatial location and star system projection state. |
| `ship` | `ShipProjection` | `<computed>` | *state-internal* | Active ship hardware, loadout, and cockpit telemetry state. |
| `sequence_number` | `int` | `0` | *state-internal* | Monotonically increasing counter of processed events. |
| `last_event_name` | `str` | `""` | *state-internal* | Name of the most recently processed journal/telemetry event. |
| `last_event_timestamp` | `str` | `""` | *state-internal* | Timestamp string emitted on the most recent event packet. |
| `additional_metadata` | `dict[str, Any]` | `<computed>` | *state-internal* | Extensible metadata dictionary for companion extensions. |

---
