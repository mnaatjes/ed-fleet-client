---
title: "ADR 0003: Submodule Migration and Hexagonal Architectural Realignment Plan"
status: "accepted"
date: "2026-11-13"
tags: ["architecture", "adr", "migration", "hexagonal", "subsystems", "ed-fleet-client", "realignment"]
---

# ADR 0003: Submodule Migration and Hexagonal Architectural Realignment Plan

## 1. Context and Problem Statement

During prototyping in `ed-integration-smoke`, seven prototype submodules were developed to establish end-to-end integration across the *Elite Dangerous* software fleet:
* `src/ed_dispatcher`: Type-safe observer and event dispatch engine.
* `src/ed_reducer`: Pure-functional state reducer engine projecting unified `FleetState`.
* `src/ed_services`: Specialized domain calculation engines (orbital, navigation, flight, combat).
* `src/ed_hydrator`: Raw JSON to typed `ed-models` domain entity hydrator.
* `src/ed_stream_monitor`: Server-Sent Events (SSE) monitor and file watcher.
* `src/ed_telemetry_client`: Low-level HTTP transport client connecting to telemetry REST APIs.
* `src/ed_fleet_client`: Prototype unified client facade coordinating the above components.

With the formal establishment of the dedicated `ed-fleet-client` repository (governed by [ADR 0001](0001_high_level_architecture.md) and [ADR 0002](0002_scope_boundaries_and_automated_enforcement.md)), we require an authoritative architectural plan for copying, migrating, and refactoring these prototype submodules into the target hexagonal package structure (`src/ed_fleet_client/{core,adapters,bootstrap}`).

---

## 2. Decision Drivers

* **Hexagonal Boundary Conformance:** Relocate source files strictly into their governing hexagonal layer (Core Domain, Ports, Adapters, Bootstrap) to satisfy ImportLinter and Pytest-Archon boundary gates.
* **Preservation of Proven Logic:** Retain the working state reduction algorithms, mutex invariant gates, observer registries, and orbital calculations developed during integration testing.
* **Elimination of Artificial Internal Package Boundaries:** Transition from separate inter-package imports (`from ed_dispatcher import ...`) to clean, unified package namespaces (`from ed_fleet_client.core.domain.dispatcher import ...`).
* **Test Suite Cohesion:** Migrate and consolidate the 49 unit and integration tests across the prototype packages into `tests/unit/` and `tests/integration/`.

---

## 3. Decision Outcome

Chosen Option: **Systematic Realignment into Layered Hexagonal Namespaces**.

The migration decomposes and maps each prototype submodule into the target repository topology:

```text
ed-fleet-client/src/ed_fleet_client/
├── core/
│   ├── domain/                               <-- Pure Domain Logic (Zero External Dependencies)
│   │   ├── dispatcher/                       <-- from ed_dispatcher (dispatcher.py, models.py)
│   │   ├── state/                            <-- from ed_reducer (engine.py, reducers.py, models.py)
│   │   └── services/                         <-- from ed_services (navigation, orbital, combat, flight)
│   ├── ports/                                <-- Abstract Contracts (Protocols & ABCs)
│   │   ├── driving/                          <-- Inward Contracts (ClientFacadePort, StreamIngestionPort)
│   │   └── driven/                           <-- Outward Contracts (TelemetryTransportPort, StoragePort)
│   └── use_cases/                            <-- Application Orchestrators (UC-01 to UC-04)
│       ├── stream_and_reduce_telemetry.py    <-- Implements UC-01
│       ├── dispatch_domain_events.py         <-- Implements UC-02
│       ├── hydrate_snapshot_data.py          <-- Implements UC-03
│       └── calculate_orbital_metrics.py      <-- Implements UC-04
├── adapters/
│   ├── driving/                              <-- Inbound Technical Adapters
│   │   ├── hydrator/                         <-- from ed_hydrator (hydrator.py, models.py)
│   │   └── stream/                           <-- from ed_stream_monitor (monitor.py, models.py)
│   └── driven/                               <-- Outbound Technical Adapters
│       └── telemetry_http/                   <-- from ed_telemetry_client (client.py, middleware.py)
├── bootstrap/                                <-- Composition Root & Dependency Injection
│   └── container.py                          <-- Wires adapters to ports
└── client.py                                 <-- High-Level Public SDK Facade (EliteDangerousClient)
```

---

## 4. Submodule-by-Submodule Migration Specification

### 4.1 `ed_dispatcher` $\to$ `core/domain/dispatcher/`
* **Source:** `src/ed_dispatcher/ed_dispatcher/{dispatcher.py, models.py}`
* **Destination:** `src/ed_fleet_client/core/domain/dispatcher/`
* **Refactoring:** Update imports from `ed_dispatcher.models` to `.models`. Remove external dependencies; preserve type-safe generic typing (`EventHandler[E]`, `Subscription`).
* **Tests:** `src/ed_dispatcher/tests/test_dispatcher.py` $\to$ `tests/unit/core/test_dispatcher.py`.

### 4.2 `ed_reducer` $\to$ `core/domain/state/`
* **Source:** `src/ed_reducer/ed_reducer/{engine.py, reducers.py, models.py}`
* **Destination:** `src/ed_fleet_client/core/domain/state/`
* **Refactoring:** Update internal module references. Formalize the Mutex Invariant validation gate (derived from ADR 0014 and Research 0001) as a pre-reducer pipeline step in `engine.py`.
* **Tests:** `src/ed_reducer/tests/{test_engine.py, test_reducers.py}` $\to$ `tests/unit/core/{test_state_engine.py, test_reducers.py}`.

### 4.3 `ed_services` $\to$ `core/domain/services/`
* **Source:** `src/ed_services/ed_services/{base.py, models.py, navigation.py, orbital.py, astrophysics.py, flight_performance.py, combat_analytics.py}`
* **Destination:** `src/ed_fleet_client/core/domain/services/`
* **Refactoring:** Change imports of `ed_dispatcher` and `ed_reducer` to relative imports within `core.domain`: `from ..dispatcher import ...` and `from ..state import ...`.
* **Tests:** `src/ed_services/tests/{test_navigation.py, test_orbital.py, test_analytics.py}` $\to$ `tests/unit/core/services/`.

### 4.4 `ed_hydrator` $\to$ `adapters/driving/hydrator/`
* **Source:** `src/ed_hydrator/ed_hydrator/{hydrator.py, models.py}`
* **Destination:** `src/ed_fleet_client/adapters/driving/hydrator/`
* **Refactoring:** Implement driving port `core/ports/driving/hydrator_port.py`. Update references to companion snapshot models (`ExtendedMarket`, etc.) and support resilient parsing (`extra="allow"` per RISK-03).
* **Tests:** `src/ed_hydrator/tests/test_hydrator.py` $\to$ `tests/unit/adapters/test_hydrator.py`.

### 4.5 `ed_stream_monitor` $\to$ `adapters/driving/stream/`
* **Source:** `src/ed_stream_monitor/ed_stream_monitor/{monitor.py, models.py}`
* **Destination:** `src/ed_fleet_client/adapters/driving/stream/`
* **Refactoring:** Implement driving stream port `core/ports/driving/stream_port.py`. Replace hardcoded imports of `ed_telemetry_client` with the driven transport port interface.
* **Tests:** `src/ed_stream_monitor/tests/test_monitor.py` $\to$ `tests/unit/adapters/test_stream_monitor.py`.

### 4.6 `ed_telemetry_client` $\to$ `adapters/driven/telemetry_http/`
* **Source:** `src/ed_telemetry_client/ed_telemetry_client/{client.py, middleware.py, models.py}`
* **Destination:** `src/ed_fleet_client/adapters/driven/telemetry_http/`
* **Refactoring:** Implement driven port `core/ports/driven/telemetry_transport_port.py`. Decouple concrete HTTP calls to satisfy `use_case_transport_isolation` and `core_domain_isolation`.
* **Tests:** `src/ed_telemetry_client/tests/test_client.py` $\to$ `tests/unit/adapters/test_telemetry_http_client.py`.

### 4.7 `ed_fleet_client` (Facade) $\to$ `client.py` & `bootstrap/container.py`
* **Source:** `src/ed_fleet_client/ed_fleet_client/client.py`
* **Destination:** `src/ed_fleet_client/client.py` (facade) and `src/ed_fleet_client/bootstrap/container.py` (wiring).
* **Refactoring:** Refactor `EliteDangerousClient` to depend strictly on Ports rather than concrete Adapter classes. Use `container.py` as the composition root to wire concrete stream monitors and HTTP clients into the facade.
* **Tests:** `src/ed_fleet_client/tests/test_client_facade.py` $\to$ `tests/integration/test_client_facade.py`.

---

## 5. Execution Sequence & Quality Gates

The migration must be executed in the following phased sequence:
1. **Phase 1: Dependencies Installation:** Add `ed-models` and `ed-transport` to `pyproject.toml` in `ed-fleet-client` and run `uv sync`.
2. **Phase 2: Core Domain Realignment:** Copy and refactor `ed_dispatcher`, `ed_reducer`, and `ed_services` into `core/domain/`. Verify that all domain tests pass and `lint-imports` confirms zero external dependencies.
3. **Phase 3: Ports & Use Cases Definition:** Author formal abstract protocols in `core/ports/{driving,driven}/` and orchestrator use cases implementing UC-01 through UC-04.
4. **Phase 4: Adapters Realignment:** Copy and refactor `ed_hydrator`, `ed_stream_monitor`, and `ed_telemetry_client` into `adapters/{driving,driven}/`.
5. **Phase 5: Composition Root & Facade Integration:** Wire all components in `bootstrap/container.py` and instantiate `EliteDangerousClient` in `client.py`.
6. **Phase 6: Quality Verification:** Run `uv run python scripts/verify.py` to ensure pre-commit, ImportLinter, MyPy static typing, and all Pytest unit/boundary/integration tests pass cleanly.

---

## 6. Consequences & Trade-offs

* **Positive:**
  - Consolidates 7 fragmented prototype modules into a single, cohesive, production-grade SDK package.
  - Guarantees strict hexagonal boundary enforcement via automated gating.
  - Preserves 100% of tested domain and integration capabilities developed in prototyping.
* **Negative:**
  - Requires updating all relative and package import statements across ~25 Python files.
  - Requires careful port decoupling to ensure `ed_stream_monitor` depends on abstract transport ports rather than concrete HTTP clients.
