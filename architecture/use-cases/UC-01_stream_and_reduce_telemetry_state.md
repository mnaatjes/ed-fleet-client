---
title: "Use-Case Specification: UC-01 Stream and Reduce Telemetry State"
use_case_id: "UC-01"
status: "approved"
version: "1.0.0"
level: "sea_level"
primary_actor: "Consumer Application (Dashboard, Overlay, CLI)"
created_at: "2026-11-13"
last_updated_at: "2026-11-13"
tags: ["use-case", "requirements", "telemetry", "state-engine", "mutex", "reduction"]
---

# Use-Case Specification: UC-01 Stream and Reduce Telemetry State

## 1. System Boundary and Scope

```text
+-----------------------------------------------------------------------------------+
| System Boundary: ed-fleet-client (State Engine & Telemetry Stream Core)           |
|                                                                                   |
|  [Actor: Consumer Application]                                                    |
|       |                                                                           |
|       | 1. client.start_stream()                                                  |
|       | 2. client.get_state()                                                     |
|       v                                                                           |
|  +--------------------+    +---------------------+    +------------------------+  |
|  | Stream Ingestion   | -> | Mutex Invariant Gate| -> | State Reducer Engine   |  |
|  +--------------------+    +---------------------+    +------------------------+  |
|                                                                    |              |
|                                                                    v              |
|                                                         [Projected FleetState]    |
|                                                         (Thread-Safe Immutable)   |
+-----------------------------------------------------------------------------------+
```

### 1.1 In-Scope
* Ingesting high-frequency continuous cockpit status updates (`StatusFlags`, `StatusFlags2`).
* Verifying incoming bitframes against the physical Mutual Exclusion (Mutex) Invariant Matrix.
* Incrementally folding valid status updates and journal events into a materialized `FleetState`.
* Providing thread-safe read access to the current vessel state (spatial regime, coordinates, gear status).

### 1.2 Out-of-Scope
* Rendering graphical UI widgets (owned by downstream client applications).
* Directly hosting network sockets on port 8080 (owned by `ed-telemetry` daemon).

---

## 2. Actors and Stakeholders

* **Primary Actor:** Consumer Application (third-party cockpit overlay, web dashboard, or bot).
* **Stakeholder (Application Developer):** Requires sub-millisecond, thread-safe access to a consistent, uncorrupted flight state without manually parsing raw bitmasks.

---

## 3. Pre-conditions and Post-conditions

### 3.1 Pre-conditions
1. `EliteDangerousClient` facade is instantiated with a valid telemetry source configuration.
2. The telemetry source (local journal files or remote REST daemon) is accessible.

### 3.2 Post-conditions
1. **Success:** `FleetState` accurately mirrors real-time vessel state in memory; changes trigger state-listener notifications.
2. **Failure:** Corrupt or out-of-order frames violating physical mutual exclusion rules are rejected at the gate and recorded in an anomaly counter; previous valid state remains preserved.

---

## 4. Main Success Scenario (Basic Flow)

1. The consumer initializes `EliteDangerousClient` and starts telemetry streaming.
2. The stream ingestion port receives a new status frame.
3. The Mutex Invariant Gate checks the active bit flags:
   - Verifies exactly one spatial flight regime is active (`DOCKED`, `LANDED`, `SUPERCRUISE`, `GLIDE_MODE`, or `NORMAL_SPACE`).
   - Verifies hardware interlocks (e.g. `SUPERCRUISE` does not assert `LANDING_GEAR`).
4. The frame satisfies all invariants.
5. The State Reducer Engine applies the new flags to `FleetState`.
6. The consumer queries `client.get_state()` and receives the updated, validated state.

---

## 5. Extensions (Alternative Flows)

* **3a. Telemetry Frame Violates Mutual Exclusion Invariant:**
  1. The frame asserts impossible conditions (e.g., both `DOCKED` and `SUPERCRUISE` are true).
  2. The gate rejects the malformed frame.
  3. The system increments the `corrupt_frame_count` metric and logs a diagnostic warning.
  4. The existing valid `FleetState` remains unchanged, and execution resumes at Step 2.
* **2a. Telemetry Source Temporarily Unavailable:**
  1. Network request times out or stream disconnects.
  2. The ingestion port enters reconnect backoff mode without crashing the client application.
  3. Stored `FleetState` marks connection status as `STALE`.
