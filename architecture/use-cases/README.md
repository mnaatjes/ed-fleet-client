---
title: "Use-Case Directory Governance and Index"
tags: ["architecture", "use-cases", "governance", "index"]
created_at: "2026-11-13"
last_updated_at: "2026-11-13"
---

# Use-Case Directory Governance and Index

Governed by the Rational Unified Process (RUP) Requirements Discipline and Alistair Cockburn's Sea-Level Goal Hierarchy.

---

## 1. Principles & Quality Invariants

1. **Black-Box System Boundary:** Specify *what* the system does from the outside in (inputs, observable state changes, and responses). Strictly omit internal code mechanisms or private classes.
2. **Sea-Level (User-Goal) Scoping:** Every use case satisfies the *Coffee Break Test*: an elementary business process completed in a single session by a single primary actor yielding measurable value.
3. **Mandatory Event Flow Decomposition:**
   * **Basic Flow (Main Success Scenario):** The standard, error-free execution path.
   * **Alternative Flows (Extensions):** Numbered recovery branches, exception handlers, and failure exits (e.g., `3a`, `4b`).
   * **Pre-conditions & Post-conditions:** Guarantees that must hold before entry and after completion.

---

## 2. Use-Case Catalog

| ID | Title | Level | Status | Primary Actor | Description |
| :---: | :--- | :---: | :---: | :--- | :--- |
| [UC-01](UC-01_stream_and_reduce_telemetry_state.md) | Stream and Reduce Telemetry State | Sea-Level | **Approved** | Consumer Application | Continuously ingest live telemetry status flags and project a valid `FleetState`. |
| [UC-02](UC-02_dispatch_domain_events_to_observers.md) | Dispatch Domain Events to Observers | Sea-Level | **Approved** | Consumer Application | Register typed event listeners and receive strongly typed domain events. |
| [UC-03](UC-03_hydrate_snapshot_and_market_data.md) | Hydrate Snapshot and Market Data | Sea-Level | **Approved** | Consumer Application | Ingest in-place companion snapshot files into extended domain DTOs. |
| [UC-04](UC-04_calculate_orbital_and_nav_metrics.md) | Calculate Orbital and Navigation Metrics | Sea-Level | **Approved** | Consumer Application | Compute real-time orbital mechanics, jump arrival ETAs, and journey progress. |
