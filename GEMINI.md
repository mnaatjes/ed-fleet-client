# Context & Developer Environment Guide: `ed-fleet-client`

## 1. Project Overview & Boundaries
`ed-fleet-client` is a Python client library providing an asynchronous control plane and reactive state projection layer for the *Elite Dangerous* telemetry fleet ecosystem.

It adheres strictly to **Hexagonal Architecture (Ports and Adapters)** with automated boundary enforcement:
- **Core Domain:** (`src/ed_fleet_client/core/`) Contains domain models, state engine, event dispatcher, and 5 domain services (`astrophysics`, `combat_analytics`, `flight_performance`, `navigation`, `orbital`). Zero external dependencies.
- **Ports:** (`src/ed_fleet_client/core/ports/`) Pure abstract interfaces for driving (hydrator, stream) and driven (transport) boundaries.
- **Adapters:** (`src/ed_fleet_client/adapters/`) Driving adapters (`facade.py`, `hydrator.py`, `stream_monitor.py`) and driven adapters (`telemetry_http_client.py`).
- **Composition Root:** (`src/ed_fleet_client/bootstrap/container.py`) Factory wiring all adapters, use cases, and services into `EliteDangerousClient`.

---

## 2. Python Environment & Standard Tooling Paths

The project uses a local virtual environment located at `.venv/` in the repository root:

* **Python Interpreter:** `.venv/bin/python`
* **Pytest:** `.venv/bin/pytest`
* **Ruff (Linter & Formatter):** `.venv/bin/ruff`
* **Type Checker:** `.venv/bin/mypy`
* **Import Linter:** `.venv/bin/lint-imports`
* **Quality Gate Runner:** `.venv/bin/python scripts/verify.py`

---

## 3. Most Recent Work & Current State (2026-11-22)

### A. Deterministic Telemetry Property-to-Event Mapping Pipeline
- **Approved ADR:** [`architecture/adr/0005_property_event_fidelity_mapping_pipeline.md`](architecture/adr/0005_property_event_fidelity_mapping_pipeline.md)
- **Approved SDD:** [`architecture/designs/0006_property_event_fidelity_mapping_pipeline.md`](architecture/designs/0006_property_event_fidelity_mapping_pipeline.md)
- **Core Modules:** Implemented under `scripts/pipeline/`:
  - `version_validator.py`: Enforces strict matching between `pyproject.toml` (`[tool.uv.sources.ed-models]`) and installed `ed-models` version.
  - `schema_inspector.py`: AST reflection of all 287 `ed-models` dataclasses and events across 566 properties.
  - `corpus_miner.py`: Calculates event cadence ($\lambda$), inter-arrival times ($\Delta t$), and concurrency overlap.
  - `fidelity_scorer.py`: Computes composite fidelity scores ($S_{\text{fidelity}} = 0.35C + 0.30U + 0.20A + 0.15R$).
  - `artifact_synthesizer.py`: Generates traversible JSON and dual-plane Markdown reference tables.
- **CLI Runner:** [`scripts/map_property_event_matrix.py`](scripts/map_property_event_matrix.py) (run via `.venv/bin/python scripts/map_property_event_matrix.py`).

### B. Generated Reference & Architectural Artifacts
1. **Machine-Readable Graph:** [`architecture/reference/data/property_event_matrix.v0.2.1.json`](architecture/reference/data/property_event_matrix.v0.2.1.json)
2. **Internal Engineering Matrix:** [`architecture/reference/property_fidelity_matrix.md`](architecture/reference/property_fidelity_matrix.md) (identifies reducer coverage and fallback rankings).
3. **Diataxis Developer Guide:** [`docs/reference/canonical_property_map.md`](docs/reference/canonical_property_map.md) (quick lookup for projection paths vs. async primary/fallback event subscriptions).
4. **Automated Test Suite:** [`tests/architecture/test_property_event_matrix.py`](tests/architecture/test_property_event_matrix.py).

### C. Future / Draft ADR
- [`architecture/adr/drafts/empirical_telemetry_ingestion_and_bayesian_smoothing.md`](architecture/adr/drafts/empirical_telemetry_ingestion_and_bayesian_smoothing.md): Specifies future pluggable ingestion from `ed-telemetry` DB / REST APIs, conjugate Gamma-Poisson Bayesian smoothing to prevent $0.00$ scores, and role-conditioned flight regime windows.

---

## 4. Key Execution Procedures

### Run Complete Downstream Quality Gates
```bash
.venv/bin/python scripts/verify.py
```
*(Runs pre-commit hooks, import-linter boundary contracts, mypy static typing, and all 73 pytest tests).*

### Re-run Property Mapping Pipeline
Whenever upstream `ed-models` dependency is upgraded in `pyproject.toml`:
```bash
.venv/bin/python scripts/map_property_event_matrix.py
```

### Run Architecture Tests
```bash
.venv/bin/pytest tests/architecture/
```

---

## 5. Next Steps for Next Session
1. **Facade Convenience Methods (Derivation):** Deriving developer convenience methods on `EliteDangerousClient` (e.g. `client.get_current_system()`, `client.get_current_ship()`) backed by the authoritative primary sources discovered in `property_event_matrix.json`.
2. **Reducer Coverage Expansion:** Implementing missing reducers in `src/ed_fleet_client/core/reducers/` for high-value properties marked as `*unmapped*` in `property_fidelity_matrix.md` (e.g. market, faction allegiance, economy).
