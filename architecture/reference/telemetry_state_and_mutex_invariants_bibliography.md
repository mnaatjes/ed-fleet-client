---
title: "Bibliography & Source Index: Telemetry State Reduction, Mutual-Exclusion (Mutex) Invariants, and Causal Lifecycles"
tags: ["architecture", "reference", "bibliography", "reducers", "invariants", "mutex", "research"]
created_at: "2026-11-24"
last_updated_at: "2026-11-24"
---

# Bibliography & Source Index: Telemetry State Reduction, Mutual-Exclusion (Mutex) Invariants, and Causal Lifecycles

This document provides an exhaustive bibliography and cross-repository index of the empirical research, mathematical models, architectural decision records (ADRs), and data artifacts that define state reduction logic, flight regime mutual exclusivity (mutex), and telemetry validation across the *Elite Dangerous* fleet ecosystem.

---

## 1. Executive Directory Index Across Repositories

| Repository | Primary Contribution | Key Artifact Types |
| :--- | :--- | :--- |
| **[`ed-integration-smoke`](file:///home/michael/src/github.com/mnaatjes/ed-integration-smoke/)** | **Authoritative Research & Empirical Discovery Hub** | Core Research Papers (0001–0003), Mutex Invariant Datasets (`.json`), Mutex Heat Matrix (`.md`), Lifecycle State DAGs (`.mmd`), Reducer RFCs/ADRs. |
| **[`ed-resolver`](file:///home/michael/src/github.com/mnaatjes/ed-resolver/)** | **Early State Store & Reduction Pipeline Prototypes** | ADRs on In-Memory State Store, Atomic Swaps, and Initial Event Reduction Pipelines. |
| **[`ed-fleet-client`](file:///home/michael/src/github.com/mnaatjes/ed-fleet-client/) (Current)** | **Production Hexagonal Implementation & Pipeline** | `validate_mutex_invariants()` Invariant Gate, Pure Reducers, AST Property Matrix, Ingestion Primers. |

---

## 2. Source Documents: Research Papers & Empirical Findings

### A. [`ed-integration-smoke/architecture/research/0001_domain_topology_causal_lifecycles_and_mutex_invariants.md`](file:///home/michael/src/github.com/mnaatjes/ed-integration-smoke/architecture/research/0001_domain_topology_causal_lifecycles_and_mutex_invariants.md)
* **Title:** *Systematic Domain Topology, Causal Lifecycles, and Invariant Mutex Mapping*
* **Date:** 2026-11-10 | **Status:** Complete
* **Core Concepts Represented:**
  * **Static Schema Key Correlation:** AST reflection over 285 event classes identifying shared primary/foreign keys (`SystemAddress`, `MarketID`, `BodyID`) and calculating domain cardinality.
  * **Causal Event Sequences:** Directed Acyclic Graphs (DAGs) capturing irreversible temporal transitions (e.g., Docking clearance sequence $\to$ touchdown $\to$ docked state).
  * **Status-to-Journal Triggers:** Mapping continuous cockpit bitmask flags flipping on/off to their corresponding discrete journal event emissions.
  * **Physical Mutual Exclusion (Mutex):** Establishing the fundamental laws of mutually exclusive gameplay states that prevent corrupted telemetry frames from polluting client state.

### B. [`ed-integration-smoke/architecture/research/0002_findings_and_cross_package_implications.md`](file:///home/michael/src/github.com/mnaatjes/ed-integration-smoke/architecture/research/0002_findings_and_cross_package_implications.md)
* **Title:** *Empirical Research Findings and Cross-Package Architecture Implications*
* **Date:** 2026-11-10 | **Status:** Complete
* **Core Concepts Represented:**
  * **Telemetry Race Conditions:** Documents the out-of-order packet arrival bugs observed during game crashes or network reconnections.
  * **Cross-Package Architectural Boundary Rules:** Establishes why state reduction must live in a dedicated domain layer decoupled from transports (`ed-telemetry`) and UI bindings (`ed-ui`).

### C. [`ed-integration-smoke/architecture/research/0003_fleet_architecture_implications_guide.md`](file:///home/michael/src/github.com/mnaatjes/ed-integration-smoke/architecture/research/0003_fleet_architecture_implications_guide.md)
* **Title:** *Fleet Architecture Implications & Integration Guide*
* **Date:** 2026-11-10 | **Status:** Complete
* **Core Concepts Represented:**
  * Guidance on applying invariant gates at the boundary of downstream SDK clients.
  * How to construct pure functional slice reducers that avoid memory leaks and maintain deterministic projections.

---

## 3. Data Artifacts: Invariant Rulesets & Mutex Matrices

### A. [`ed-integration-smoke/architecture/reference/data/mutex_matrix_heat.md`](file:///home/michael/src/github.com/mnaatjes/ed-integration-smoke/architecture/reference/data/mutex_matrix_heat.md)
* **Title:** *Mutual Exclusion (Mutex) Invariants in Elite Dangerous*
* **Core Data Represented:**
  * **Flight Regime Partitions:** Proves that a vessel can occupy strictly one flight regime at any given millisecond:
    $$\text{Regime} \in \{\text{DOCKED}, \text{LANDED}, \text{SUPERCRUISE}, \text{GLIDE\_MODE}, \text{NORMAL\_SPACE}\}$$
  * **Cockpit Hardware Interlocks:** Truth matrix of physical hardware inhibitions:
    * `SUPERCRUISE` strictly excludes `HARDPOINTS_DEPLOYED`, `LANDING_GEAR_DOWN`, `CARGO_SCOOP_DEPLOYED`, `DOCKED`, `LANDED`.
    * `DOCKED` strictly excludes `SUPERCRUISE`, `HARDPOINTS_DEPLOYED`, `FLIGHT_ASSIST_OFF`, `IN_WING`, `SCOOPING_FUEL`.
    * `LANDED` strictly excludes `SUPERCRUISE`, `SCOOPING_FUEL`.
    * `SILENT_RUNNING` strictly excludes `SHIELDS_UP`.
    * `ON_FOOT` strictly excludes `IN_SRV`, `SUPERCRUISE`, and all cockpit flight deployables.
  * **Transactional Event Inversion Pairs:** Formal list of inverse event cancellations:
    * `(Docked, Undocked)`
    * `(SupercruiseEntry, SupercruiseExit)`
    * `(Touchdown, Liftoff)`
    * `(Disembark, Embark)`
    * `(Interdicted, EscapeInterdiction)`
    * `(ApproachBody, LeaveBody)`

### B. [`ed-integration-smoke/architecture/reference/data/mutex_invariants.json`](file:///home/michael/src/github.com/mnaatjes/ed-integration-smoke/architecture/reference/data/mutex_invariants.json)
* **Title:** *Machine-Readable Mutex Invariant Contract (v1.0.0)*
* **Core Data Represented:**
  * JSON Schema defining the 5 primary flight regimes, 5 hardware interlock sets, and 6 event inversion pairs.
  * Consumed by automated test suites to validate invariant gate implementations.

### C. [`ed-integration-smoke/architecture/reference/data/lifecycle_workflows.mmd`](file:///home/michael/src/github.com/mnaatjes/ed-integration-smoke/architecture/reference/data/lifecycle_workflows.mmd)
* **Title:** *Flight Lifecycle State Transition Diagrams*
* **Core Data Represented:**
  * Mermaid state diagrams modeling valid transitions between `NormalSpace`, `Supercruise`, `Hyperdrive`, `OrbitalGlide`, `SurfaceTouchdown`, and `StationDock`.

---

## 4. Architectural Decision Records (ADRs) & RFCs

### In `ed-integration-smoke`:
* [`architecture/adr/0010_event_driven_state_reducer_engine.md`](file:///home/michael/src/github.com/mnaatjes/ed-integration-smoke/architecture/adr/0010_event_driven_state_reducer_engine.md):
  * **Decision:** Replaced monolithic in-place mutable dictionaries with modular slice reducers (`location`, `ship`, `session`) yielding immutable dataclass projections.
  * **Key Concept:** Established the pure functional signature $(\text{State}, \text{Event}) \to \text{New State}$.
* [`architecture/rfcs/0002_domain_aware_predictive_lifecycle_and_mutex_resilience.md`](file:///home/michael/src/github.com/mnaatjes/ed-integration-smoke/architecture/rfcs/0002_domain_aware_predictive_lifecycle_and_mutex_resilience.md):
  * **Proposal:** Implemented invariant gating ahead of reduction to detect and drop contradictory telemetry packets.
* [`architecture/adr/0014_systematic_domain_relationship_discovery_architecture.md`](file:///home/michael/src/github.com/mnaatjes/ed-integration-smoke/architecture/adr/0014_systematic_domain_relationship_discovery_architecture.md):
  * **Decision:** Outlined the AST mining framework used to discover entity-relationship graphs and event correlations from `ed-models`.

### In `ed-resolver`:
* [`architecture/adr/0007_in_memory_domain_state_store_and_atomic_swap.md`](file:///home/michael/src/github.com/mnaatjes/ed-resolver/architecture/adr/0007_in_memory_domain_state_store_and_atomic_swap.md):
  * **Decision:** Early prototype establishing atomic reference swapping for state store updates.
* [`architecture/adr/0008_domain_event_reduction_pipelines_and_dispatch.md`](file:///home/michael/src/github.com/mnaatjes/ed-resolver/architecture/adr/0008_domain_event_reduction_pipelines_and_dispatch.md):
  * **Decision:** Early prototype for event dispatching and the Ordering Law.

### In `ed-fleet-client` (Current Repository):
* [`architecture/adr/0001_high_level_architecture.md`](file:///home/michael/src/github.com/mnaatjes/ed-fleet-client/architecture/adr/0001_high_level_architecture.md):
  * Formalized migration of the reducer engine and invariant gates into the core hexagonal domain.
* [`architecture/adr/0005_property_event_fidelity_mapping_pipeline.md`](file:///home/michael/src/github.com/mnaatjes/ed-fleet-client/architecture/adr/0005_property_event_fidelity_mapping_pipeline.md):
  * Specified multi-vector fidelity ranking ($S_{\text{fidelity}} = 0.35C + 0.30U + 0.20A + 0.15R$) for mapping 566 properties across 287 schemas to authoritative event sources.
* [`architecture/adr/drafts/decoupling_state_and_event_client_repositories.md`](file:///home/michael/src/github.com/mnaatjes/ed-fleet-client/architecture/adr/drafts/decoupling_state_and_event_client_repositories.md):
  * Architectural blueprint decoupling state reduction (`ed-state-client`) from event pub/sub (`ed-event-client`).

---

## 5. Active Implementations & Code Verification

In the current `ed-fleet-client` codebase:
* **Invariant Gate Implementation:** [`src/ed_fleet_client/core/domain/state/engine.py`](file:///home/michael/src/github.com/mnaatjes/ed-fleet-client/src/ed_fleet_client/core/domain/state/engine.py#L23-L56) — [`validate_mutex_invariants()`](file:///home/michael/src/github.com/mnaatjes/ed-fleet-client/src/ed_fleet_client/core/domain/state/engine.py#L23-L56) actively codifies the flight regime and deployable hardware rules specified in `mutex_matrix_heat.md`.
* **State Projections:** [`src/ed_fleet_client/core/domain/state/models.py`](file:///home/michael/src/github.com/mnaatjes/ed-fleet-client/src/ed_fleet_client/core/domain/state/models.py#L1-L100) — Immutable dataclasses (`ClientStateProjection`, `LocationProjection`, `ShipProjection`, `SessionProjection`).
* **Pure Reducers:** [`src/ed_fleet_client/core/domain/state/reducers.py`](file:///home/michael/src/github.com/mnaatjes/ed-fleet-client/src/ed_fleet_client/core/domain/state/reducers.py#L1-L120) — Synchronous pure reducers for location, ship hardware/telemetry, and session.
* **Property Coverage Matrix:** [`architecture/reference/property_fidelity_matrix.md`](file:///home/michael/src/github.com/mnaatjes/ed-fleet-client/architecture/reference/property_fidelity_matrix.md) — Live coverage matrix generated by AST reflection.
