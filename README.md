# ed-fleet-client

Unified reactive client SDK and state facade for Elite Dangerous telemetry services

## Architectural Governance
This service is architected in accordance with Hexagonal Architecture (Ports and Adapters).
* Core Domain logic resides in `src/ed_fleet_client/core/` with ZERO external infrastructure dependencies.
* Architectural boundaries are enforced deterministically via `import-linter` and `pytest-archon`.

## Quickstart

Run quality verification gates:
```bash
uv run python scripts/verify.py
```
