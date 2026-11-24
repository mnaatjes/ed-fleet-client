# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- Replaced hardcoded `PROJECTION_TARGET_MAP` with dynamic dataclass schema reflection in `scripts/pipeline/schema_inspector.py`, automatically introspecting `ClientStateProjection` and child projections (Resolves #11, PR #12).
- Added `ship_id` and `hull_health` attributes to `ShipProjection` and unpacked them in `reduce_ship()` from `Loadout` events.
- Added Addenda 1, 2, and 3 to `architecture/adr/0005_property_event_fidelity_mapping_pipeline.md` formalizing dynamic dataclass introspection, deterministic Diataxis Reference generation, and event-only streaming cataloging.
- Added field metadata annotations across all domain projection models in `src/ed_fleet_client/core/domain/state/models.py`.
- Added deterministic Diataxis Reference generator for materialized state projections and reducers (`docs/reference/state_projections_and_reducers.md`) (Resolves #13, PR #14).
- Added deterministic Diataxis Reference catalog of event-only (unmapped) telemetry properties (`docs/reference/event_streaming_catalog.md`).
- Added Diataxis Explanation guide `docs/explanation/telemetry_pipeline_and_state_hierarchy.md` detailing the 4-stage hierarchy from raw wire payload, schema contract, async event dispatch, to pure reducer state projections.
- Added comprehensive engineering primer `architecture/notes/event_driven_telemetry_and_state_fundamentals.md` covering EDA best practices, state stores, the Ordering Law, game loops, and asynchronous push vs. pull taxonomies (PR #15).
- Implemented deterministic telemetry property-to-event derivation and fidelity pipeline (`scripts/map_property_event_matrix.py` and `scripts/pipeline/`) governed by ADR 0005 and SDD 0006.
- Added upstream version validator enforcing strict pinning against `ed-models` revision in `pyproject.toml`.
- Added multi-vector fidelity scoring engine ($S_{\text{fidelity}} = 0.35C + 0.30U + 0.20A + 0.15R$) evaluating completeness, uniqueness, timing phase accuracy, and cadence.
- Generated machine-readable traversible JSON graph `architecture/reference/data/property_event_matrix.v0.2.1.json` across 287 schemas and 566 properties.
- Generated internal engineering coverage matrix `architecture/reference/property_fidelity_matrix.md`.
- Generated Diataxis developer reference guide `docs/reference/canonical_property_map.md` mapping properties to projection paths and authoritative event sources.
- Added automated test suite `tests/architecture/test_property_event_matrix.py` verifying matrix integrity, determinism, and version compliance.
- Added draft architecture record `architecture/adr/drafts/empirical_telemetry_ingestion_and_bayesian_smoothing.md` specifying future Bayesian smoothing and regime-conditioned empirical mining.
- Added draft architecture record `architecture/adr/drafts/decoupling_state_and_event_client_repositories.md` specifying decoupling into `ed-state-client`, `ed-event-client`, and composite `ed-fleet-sdk` facade repositories with full directory topologies, boundary models, and key-concept maps.

> Context Hydration Reference: `9acf5e6f-6a6a-4b31-8053-d855ac8f3d00`


## [0.1.2] - 2026-11-16

### Added
- Added initial state synchronization on `EliteDangerousClient.connect(sync_initial_state=True)` to seed `state_engine` from `GET /api/v1/state` prior to stream processing.
- Added historical frame filtering in `StreamMonitor` (`StreamMonitorConfig.filter_historical=True` and `since_timestamp`) to drop pre-connection events from replay buffers.
- Added `fetch_state()` method to `TelemetryTransportPort` and `TelemetryHttpClient`.
- Exported `StreamMonitorConfig` from top-level `ed_fleet_client`.

## [0.1.1] - 2026-11-16

### Fixed
- Fixed SSE journal and status payload hydration in `TelemetryDomainHydrator` by supporting `"payload"` in addition to `"payload_json"`.
- Fixed event propagation in `EliteDangerousClient._handle_raw_event` to dispatch hydrated domain events to subscribers.

## [0.1.0] - 2026-11-15

### Added
- Hexagonal architecture scaffold with `import-linter` and `pytest` AST boundary enforcement.
- Core domain migration (`ed_dispatcher`, `ed_reducer` with Mutex Invariant gate, and all 5 `ed_services`).
- Driving and driven ports (`HydratorPort`, `StreamIngestionPort`, `ClientFacadePort`, `TelemetryTransportPort`) and `UC-01`–`UC-04` use cases.
- Driving adapters (`TelemetryDomainHydrator`, `StreamMonitor`, `EliteDangerousClient` facade) and driven adapter (`TelemetryHttpClient` with SSE streaming).
- Composition root (`bootstrap/container.py`) wiring all adapters, use cases, and domain services.
- Diataxis documentation under `docs/` (`tutorials/`, `how-to/`, `reference/`).
