---
title: "Use-Case Specification: UC-03 Hydrate Snapshot and Market Data"
use_case_id: "UC-03"
status: "approved"
version: "1.0.0"
level: "sea_level"
primary_actor: "Consumer Application"
created_at: "2026-11-13"
last_updated_at: "2026-11-13"
tags: ["use-case", "requirements", "snapshots", "hydration", "market", "shipyard", "duality"]
---

# Use-Case Specification: UC-03 Hydrate Snapshot and Market Data

## 1. System Boundary and Scope

```text
+-----------------------------------------------------------------------------------+
| System Boundary: ed-fleet-client (Hydrator & Snapshot Core)                       |
|                                                                                   |
|  [Actor: Consumer Application]                                                    |
|       |                                                                           |
|       | 1. client.get_snapshot("Market" | "Shipyard" | ...)                       |
|       v                                                                           |
|  +--------------------+    +---------------------+    +------------------------+  |
|  | Snapshot Watcher   | -> | Schema Validator    | -> | Domain Hydrator        |  |
|  +--------------------+    +---------------------+    +------------------------+  |
|                                                                    |              |
|                                                                    v              |
|                                                         [Extended DTO Model]      |
|                                                         (ExtendedMarket, etc.)    |
+-----------------------------------------------------------------------------------+
```

### 1.1 In-Scope
* Ingesting in-place companion snapshot files (`Market.json`, `Shipyard.json`, `Outfitting.json`, `NavRoute.json`, `Cargo.json`, `ModulesInfo.json`, `ShipLocker.json`, `Backpack.json`, `FCMaterials.json`).
* Mapping companion journal notification events to full extended DTO models (e.g. `ExtendedMarket`).
* Applying Fleet Carrier duality rules (RES-0001): interpreting `Shipyard.json` as personal stored fleet valuations when docked at a carrier, and as retail stock when docked at a starport.
* Correlating snapshot data with existing session entities using universal Hub Keys (`MarketID`, `SystemAddress`).

### 1.2 Out-of-Scope
* Uploading commodity prices to third-party web gateways (e.g., EDDN).

---

## 2. Actors and Stakeholders

* **Primary Actor:** Consumer Application.
* **Stakeholder (Developer):** Requires reliable access to complete market listings and outfitting inventories without race conditions during disk overwrites.

---

## 3. Pre-conditions and Post-conditions

### 3.1 Pre-conditions
1. Companion snapshot files exist in the journal directory or are available via the telemetry REST API.
2. The player is in a valid operational state (e.g. `DOCKED` for Market/Shipyard).

### 3.2 Post-conditions
1. **Success:** Returns strongly typed extended models containing all items, prices, and module attributes.
2. **Failure:** If the file is being written concurrently, retry reading with exponential backoff until the file is complete and valid.

---

## 4. Main Success Scenario (Basic Flow)

1. The consumer requests market data: `client.get_snapshot("Market")`.
2. The hydrator locates and reads `Market.json`.
3. The schema validator verifies JSON syntax and model integrity.
4. The hydrator instantiates an `ExtendedMarket` model.
5. The hydrator correlates the `MarketID` with the current starport context in `FleetState`.
6. The consumer receives the fully hydrated `ExtendedMarket` object.

---

## 5. Extensions (Alternative Flows)

* **2a. Partial File Read (Concurrent Write in Progress):**
  1. The JSON parser encounters truncated data because Frontier's engine is actively writing the file.
  2. The hydrator catches the syntax error and pauses for $50\text{ ms}$.
  3. The hydrator retries the read operation up to 3 times.
  4. The complete file is read successfully, and execution resumes at Step 3.
