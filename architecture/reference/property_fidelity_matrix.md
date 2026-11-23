---
title: "Property Fidelity & Event Mapping Matrix"
tags: ["architecture", "telemetry", "fidelity", "matrix", "reference"]
created_at: "2026-11-23"
last_updated_at: "2026-11-23"
---

# Property Fidelity & Event Mapping Matrix

Generated from **`ed-models` v0.2.1** via `scripts/map_property_event_matrix.py`.

## 1. Executive Summary & Dimension Overview

- **Target Model Version:** `v0.2.1`
- **Canonical Properties Analyzed:** 566
- **Journal & Telemetry Schemas Reflected:** 287

## 2. Tier 1 & Tier 2 Canonical Navigation and Vessel State

| Canonical Property | Tier | Primary Source | Score | Projection Target | Fallback Sources |
| :--- | :---: | :--- | :---: | :--- | :--- |
| `body_id` | 1 | `ApproachBody` | 0.78 | `location.body_id` | FSDJump, LeaveBody, Liftoff |
| `body_name` | 1 | `ScanOrganic` | 0.75 | `location.body` | StatusTelemetry, ApproachBody, FSDJump |
| `cmdr_fid` | 1 | `ClearSavedGame` | 0.73 | `session.fid` | Commander, LoadGame, NewCommander |
| `cmdr_name` | 1 | `LoadGame` | 0.65 | `session.commander_name` | *none* |
| `coordinates` | 1 | `StatusTelemetry` | 0.70 | `location.star_pos` | FSDJump, CarrierJump, Location |
| `docked` | 1 | `CarrierJump` | 0.61 | `location.docked` | Location |
| `ship_id` | 1 | `FetchRemoteModule` | 0.73 | `ship.ship_id` | LoadGame, Loadout, MassModuleStore |
| `ship_ident` | 1 | `LoadGame` | 0.73 | `ship.ship_ident` | Loadout |
| `ship_model` | 1 | `FetchRemoteModule` | 0.65 | `ship.ship_type` | LoadGame, Loadout, MassModuleStore |
| `ship_name` | 1 | `LoadGame` | 0.65 | `ship.ship_name` | Loadout |
| `star_system` | 1 | `ApproachBody` | 0.69 | `location.star_system` | Docked, FSDJump, LeaveBody |
| `system_address` | 1 | `ApproachBody` | 0.78 | `location.system_address` | DiscoveryScan, Docked, FSDJump |
| `altitude` | 2 | `StatusTelemetry` | 0.80 | `ship.telemetry.altitude` | Status, Screenshot |
| `firegroup` | 2 | `StatusTelemetry` | 0.97 | `ship.telemetry.firegroup` | Status |
| `flags` | 2 | `StatusTelemetry` | 0.88 | `ship.telemetry.flags` | Status |
| `flags2` | 2 | `StatusTelemetry` | 0.88 | `ship.telemetry.flags2` | Status |
| `fuel` | 2 | `Status` | 0.70 | `ship.telemetry.fuel_main` | *none* |
| `fuel_main` | 2 | `StatusTelemetry` | 0.97 | `ship.telemetry.fuel_main` | *none* |
| `fuel_reservoir` | 2 | `StatusTelemetry` | 0.97 | `ship.telemetry.fuel_reservoir` | *none* |
| `gui_focus` | 2 | `StatusTelemetry` | 0.97 | `ship.telemetry.gui_focus` | *none* |
| `heading` | 2 | `StatusTelemetry` | 0.80 | `ship.telemetry.heading` | Status, Screenshot |
| `hull_health` | 2 | `Loadout` | 0.70 | `ship.hull_health` | ShipTargeted |
| `latitude` | 2 | `StatusTelemetry` | 0.80 | `ship.telemetry.latitude` | Status, Liftoff, Touchdown |
| `longitude` | 2 | `StatusTelemetry` | 0.80 | `ship.telemetry.longitude` | Status, Liftoff, Touchdown |
| `pips` | 2 | `StatusTelemetry` | 0.97 | `ship.telemetry.pips` | Status |

## 3. Tier 3 Contextual & Market State

| Canonical Property | Tier | Primary Source | Score | Projection Target | Fallback Sources |
| :--- | :---: | :--- | :---: | :--- | :--- |
| `allegiance` | 3 | `FSDJump` | 0.69 | `location.allegiance` | CarrierJump, Location |
| `credits` | 3 | `LoadGame` | 0.70 | `session.credits` | *none* |
| `economy` | 3 | `FSDJump` | 0.69 | `location.economy` | CarrierJump, Location |
| `government` | 3 | `FSDJump` | 0.69 | `location.government` | CarrierJump, Location |
| `loan` | 3 | `LoadGame` | 0.70 | `session.loan` | *none* |
| `market_id` | 3 | `Docked` | 0.78 | `location.market_id` | DockingCancelled, DockingDenied, DockingGranted |
| `population` | 3 | `FSDJump` | 0.75 | `location.population` | CarrierJump, Location |
| `security` | 3 | `Docked` | 0.69 | `location.security` | FSDJump, CarrierJump, Location |
| `station_name` | 3 | `Docked` | 0.69 | `location.station_name` | DockingCancelled, DockingDenied, DockingGranted |
| `station_type` | 3 | `Docked` | 0.66 | `location.station_type` | DockingCancelled, DockingDenied, DockingGranted |

## 4. Multi-Source Concurrency & Reducer Coverage

| Property | Concurrency Count | Primary Reducer Target | Reducer Status |
| :--- | :---: | :--- | :---: |
| `body_id` | 23 events | `location.body_id` | **Covered** |
| `body_name` | 16 events | `location.body` | **Covered** |
| `cmdr_fid` | 4 events | `session.fid` | **Covered** |
| `cmdr_name` | 1 events | `session.commander_name` | **Covered** |
| `coordinates` | 4 events | `location.star_pos` | **Covered** |
| `docked` | 2 events | `location.docked` | **Covered** |
| `ship_id` | 16 events | `ship.ship_id` | **Covered** |
| `ship_ident` | 2 events | `ship.ship_ident` | **Covered** |
| `ship_model` | 22 events | `ship.ship_type` | **Covered** |
| `ship_name` | 2 events | `ship.ship_name` | **Covered** |
| `star_system` | 28 events | `location.star_system` | **Covered** |
| `system_address` | 34 events | `location.system_address` | **Covered** |
| `altitude` | 3 events | `ship.telemetry.altitude` | **Covered** |
| `firegroup` | 2 events | `ship.telemetry.firegroup` | **Covered** |
| `flags` | 2 events | `ship.telemetry.flags` | **Covered** |
| `flags2` | 2 events | `ship.telemetry.flags2` | **Covered** |
| `fuel` | 1 events | `ship.telemetry.fuel_main` | **Covered** |
| `fuel_main` | 1 events | `ship.telemetry.fuel_main` | **Covered** |
| `fuel_reservoir` | 1 events | `ship.telemetry.fuel_reservoir` | **Covered** |
| `gui_focus` | 1 events | `ship.telemetry.gui_focus` | **Covered** |
| `heading` | 3 events | `ship.telemetry.heading` | **Covered** |
| `hull_health` | 2 events | `ship.hull_health` | **Covered** |
| `latitude` | 8 events | `ship.telemetry.latitude` | **Covered** |
| `longitude` | 8 events | `ship.telemetry.longitude` | **Covered** |
| `pips` | 2 events | `ship.telemetry.pips` | **Covered** |
