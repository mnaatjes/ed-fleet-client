---
title: "Canonical Property-to-Event Reference Guide"
tags: ["docs", "reference", "telemetry", "events", "properties", "projections"]
created_at: "2026-11-23"
last_updated_at: "2026-11-23"
---

# Canonical Property-to-Event Reference Guide

This guide answers the developer question: ***If I need property X, which projection holds it, and which journal/status events contribute to it?***

> [!NOTE]
> Pinned to upstream **`ed-models` v0.2.1**. Generated deterministically by the telemetry pipeline.

## 1. Quick Property Lookup

| Desired Property | Target Projection Path | Authoritative Primary Event | Fallback / Pre-Transition Events |
| :--- | :--- | :--- | :--- |
| **`body_id`** | `client.state.location.body_id` | `ApproachBody` | `FSDJump`, `LeaveBody`, `Liftoff` |
| **`body_name`** | `client.state.location.body` | `ScanOrganic` | `StatusTelemetry`, `ApproachBody`, `FSDJump` |
| **`cmdr_fid`** | `client.state.session.fid` | `ClearSavedGame` | `Commander`, `LoadGame`, `NewCommander` |
| **`cmdr_name`** | `client.state.session.commander_name` | `LoadGame` | *none* |
| **`coordinates`** | `client.state.location.star_pos` | `StatusTelemetry` | `FSDJump`, `CarrierJump`, `Location` |
| **`docked`** | `client.state.location.docked` | `CarrierJump` | `Location` |
| **`ship_id`** | `client.state.ship.ship_id` | `FetchRemoteModule` | `LoadGame`, `Loadout`, `MassModuleStore` |
| **`ship_ident`** | `client.state.ship.ship_ident` | `LoadGame` | `Loadout` |
| **`ship_model`** | `client.state.ship.ship_type` | `FetchRemoteModule` | `LoadGame`, `Loadout`, `MassModuleStore` |
| **`ship_name`** | `client.state.ship.ship_name` | `LoadGame` | `Loadout` |
| **`star_system`** | `client.state.location.star_system` | `ApproachBody` | `Docked`, `FSDJump`, `LeaveBody` |
| **`system_address`** | `client.state.location.system_address` | `ApproachBody` | `DiscoveryScan`, `Docked`, `FSDJump` |
| **`altitude`** | `client.state.ship.telemetry.altitude` | `StatusTelemetry` | `Status`, `Screenshot` |
| **`firegroup`** | `client.state.ship.telemetry.firegroup` | `StatusTelemetry` | `Status` |
| **`flags`** | `client.state.ship.telemetry.flags` | `StatusTelemetry` | `Status` |
| **`flags2`** | `client.state.ship.telemetry.flags2` | `StatusTelemetry` | `Status` |
| **`fuel`** | `client.state.ship.telemetry.fuel_main` | `Status` | *none* |
| **`fuel_main`** | `client.state.ship.telemetry.fuel_main` | `StatusTelemetry` | *none* |
| **`fuel_reservoir`** | `client.state.ship.telemetry.fuel_reservoir` | `StatusTelemetry` | *none* |
| **`gui_focus`** | `client.state.ship.telemetry.gui_focus` | `StatusTelemetry` | *none* |
| **`heading`** | `client.state.ship.telemetry.heading` | `StatusTelemetry` | `Status`, `Screenshot` |
| **`hull_health`** | `client.state.ship.hull_health` | `Loadout` | `ShipTargeted` |
| **`latitude`** | `client.state.ship.telemetry.latitude` | `StatusTelemetry` | `Status`, `Liftoff`, `Touchdown` |
| **`longitude`** | `client.state.ship.telemetry.longitude` | `StatusTelemetry` | `Status`, `Liftoff`, `Touchdown` |
| **`pips`** | `client.state.ship.telemetry.pips` | `StatusTelemetry` | `Status` |
| **`allegiance`** | `client.state.location.allegiance` | `FSDJump` | `CarrierJump`, `Location` |
| **`credits`** | `client.state.session.credits` | `LoadGame` | *none* |
| **`economy`** | `client.state.location.economy` | `FSDJump` | `CarrierJump`, `Location` |
| **`government`** | `client.state.location.government` | `FSDJump` | `CarrierJump`, `Location` |
| **`loan`** | `client.state.session.loan` | `LoadGame` | *none* |
| **`market_id`** | `client.state.location.market_id` | `Docked` | `DockingCancelled`, `DockingDenied`, `DockingGranted` |
| **`population`** | `client.state.location.population` | `FSDJump` | `CarrierJump`, `Location` |
| **`security`** | `client.state.location.security` | `Docked` | `FSDJump`, `CarrierJump`, `Location` |
| **`station_name`** | `client.state.location.station_name` | `Docked` | `DockingCancelled`, `DockingDenied`, `DockingGranted` |
| **`station_type`** | `client.state.location.station_type` | `Docked` | `DockingCancelled`, `DockingDenied`, `DockingGranted` |

## 2. Event Sourcing Behavior

### Spatial & Navigation Properties
- **`star_system` & `system_address`:** Primary authority is `FSDJump` upon hyperspace arrival. If reconnecting during an active session, `Location` hydrates initial coordinates. Transitional target is exposed early by `FSDTarget` / `StartJump`.
- **`body_name` & `body_id`:** Updated upon `ApproachBody`, `Touchdown`, or orbital telemetry transition.

### Vessel Loadout & Operations
- **`ship_model`, `ship_name`, `ship_id`:** Hydrated authoritatively by `Loadout` and `ShipyardSwap`.
- **`fuel_main` & `fuel_reservoir`:** Live streaming updates originate from continuous `StatusTelemetry`. Authoritative absolute snapshots arrive on `FuelScoop` and `RefuelAll`.

### Commander & Economy
- **`cmdr_name` & `cmdr_fid`:** Populated on `Commander` and `LoadGame` startup events.
- **`credits`:** Reflected on startup (`LoadGame`) and updated incrementally on transaction events (`MarketBuy`, `MarketSell`, `PayFines`, `RedeemVoucher`).
