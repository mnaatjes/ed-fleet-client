# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

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
