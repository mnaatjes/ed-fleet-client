---
title: "Architectural Decision Records Governance and Index"
tags: ["architecture", "adr", "governance", "index"]
created_at: "2026-11-13"
last_updated_at: "2026-11-13"
---

# Architectural Decision Records Governance and Index

Governed by Markdown Architectural Decision Records (MADR 3.0).

---

## 1. Principles & Quality Invariants

1. **Immutable Historical Record:** Once committed and marked `Accepted`, an ADR is never deleted or altered to reflect new designs.
2. **Supersedence Rule:** Reversals or migrations must be recorded as a new sequential ADR explicitly citing `supersedes: ["architecture/adr/NNNN_...md"]`.
3. **Sequential Naming:** `NNNN_descriptive_slug.md` (zero-padded 4-digit index).

---

## 2. Decision Log

| Index | Title | Status | Date | Supersedes |
| :---: | :--- | :---: | :---: | :--- |
| [0001](0001_high_level_architecture.md) | High-Level Hexagonal Architecture & Subsystem Integration | **Accepted** | 2026-11-13 | — |
| [0002](0002_scope_boundaries_and_automated_enforcement.md) | System Scope, Boundaries, and Multi-Tier Automated Enforcement | **Accepted** | 2026-11-13 | — |
| [0003](0003_submodule_migration_and_hexagonal_realignment.md) | Submodule Migration and Hexagonal Architectural Realignment Plan | **Accepted** | 2026-11-13 | — |
| [0004](0004_end_user_control_plane_facade.md) | End-User Control Plane Facade & Driving Adapters | **Accepted** | 2026-11-15 | — |
| [0005](0005_property_event_fidelity_mapping_pipeline.md) | Deterministic Telemetry Property-to-Event Derivation & Fidelity Mapping Pipeline | **Accepted** | 2026-11-22 | — |

---

## 3. Draft Architecture Records

Draft or deferred decision proposals are archived under `architecture/adr/drafts/` until scheduled for implementation:
* [`drafts/empirical_telemetry_ingestion_and_bayesian_smoothing.md`](drafts/empirical_telemetry_ingestion_and_bayesian_smoothing.md) - Empirical Flight Telemetry Ingestion, Bayesian Smoothing, and Regime-Conditioned Fidelity.
* [`drafts/decoupling_state_and_event_client_repositories.md`](drafts/decoupling_state_and_event_client_repositories.md) - Decoupling Telemetry State Projections and Event Streaming Bus into Specialized Client Repositories.
