---
title: "Master Risk Register"
tags: ["architecture", "risk", "register", "ed-fleet-client"]
created_at: "2026-11-13"
last_updated_at: "2026-11-13"
---

# Master Risk Register

Governed by Barry Boehm's Risk Exposure formula ($RE = P \times I$) and the Unified Process Inception Discipline.

---

## 1. Risk Scoring & Triage Policy

* **Probability ($P$):** Integer scale `1` (Extremely Unlikely) to `5` (Near Certainty).
* **Impact ($I$):** Integer scale `1` (Negligible / Cosmetic) to `5` (Catastrophic / Complete Outage / Data Loss).
* **Risk Exposure ($RE$):** Calculated product ($RE = P \times I$, range 1 to 25).
* **Triage Thresholds:**
  * **Critical ($RE \ge 16$):** Architectural blocker requiring immediate mitigation spike.
  * **Moderate ($9 \le RE \le 15$):** Active monitoring; mitigation plan must be drafted during Elaboration.
  * **Low ($RE < 9$):** Managed via standard development checks.

---

## 2. Active Risk Log

| Risk ID | Title & Description | $P$ | $I$ | $RE$ | Status | Mitigation Strategy |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **RISK-01** | **Telemetry Stream Desynchronization:** Rapid game transitions (e.g., emergency drops from supercruise) cause out-of-order or corrupt status bitframes to reach the reducer, projecting impossible physical states. | 3 | 4 | **12** | active | Embed the empirical Mutual Exclusion (Mutex) Invariant Matrix directly in `core/domain/state/`. Telemetry frames asserting mutually exclusive states (e.g. `DOCKED` and `SUPERCRUISE`) are rejected at the gate without corrupting `FleetState`. |
| **RISK-02** | **Remote Telemetry Daemon Unavailability:** The local or remote `ed-telemetry` REST daemon is offline, unprovisioned, or unreachable when `EliteDangerousClient` boots. | 4 | 3 | **12** | active | Decouple the client facade via `core/ports/driven/telemetry_port.py`. Support graceful degradation: automatically fall back to local direct filesystem watching (`adapters/driving/stream/`) if HTTP daemon endpoints are unreachable. |
| **RISK-03** | **Event Hydration Model Drift:** Undocumented game updates or new Odyssey journal events introduce unknown JSON schemas, causing Pydantic validation crashes during model hydration. | 3 | 4 | **12** | active | Utilize resilient schema parsing in `adapters/driving/hydrator/` with `extra="allow"` and graceful fallback to generic `RawJournalEventDTO` for unrecognized event names. |
| **RISK-04** | **High-Frequency Ingestion CPU Starvation:** Live flight status updates emitted at $\sim 4\text{ Hz}$ combined with rapid file writes create CPU bottlenecks or thread contention in the dispatcher observer loop. | 2 | 4 | **8** | active | Implement asynchronous, bounded worker queues in `core/domain/dispatcher/` with thread-safe observer dispatching, ensuring UI callbacks never block ingestion threads. |
| **RISK-05** | **Hexagonal Boundary Erosion:** Developers inadvertently import outward adapters (HTTP clients, file watchers) into the inner core domain, destroying testability and re-introducing coupling traps. | 3 | 3 | **9** | active | Enforce strict import boundary rules via `import-linter` and `pytest-archon` boundary tests in continuous integration (`tests/architecture/test_boundaries.py`). |
| **RISK-06** | **Snapshot File Write Race Conditions:** Frontier companion files (`Market.json`, `Cargo.json`) are overwritten in-place rather than appended, risking partial reads during concurrent write operations. | 3 | 3 | **9** | active | Implement retry-backoff reading with JSON parsing integrity guards and timestamp reconciliation in `adapters/driving/stream/`. Discard incomplete JSON fragments until write lock releases. |

---

## 3. Retired Risk Log

*No risks retired to date.*
