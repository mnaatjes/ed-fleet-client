---
title: "Use-Case Specification: UC-04 Calculate Orbital and Navigation Metrics"
use_case_id: "UC-04"
status: "approved"
version: "1.0.0"
level: "sea_level"
primary_actor: "Consumer Application"
created_at: "2026-11-13"
last_updated_at: "2026-11-13"
tags: ["use-case", "requirements", "navigation", "orbital", "eta", "calculations"]
---

# Use-Case Specification: UC-04 Calculate Orbital and Navigation Metrics

## 1. System Boundary and Scope

```text
+-----------------------------------------------------------------------------------+
| System Boundary: ed-fleet-client (Domain Services Core)                           |
|                                                                                   |
|  [Actor: Consumer Application]                                                    |
|       |                                                                           |
|       | 1. client.navigation.get_route_progress()                                  |
|       | 2. client.orbital.calculate_orbital_speed()                               |
|       v                                                                           |
|  +--------------------+    +---------------------+    +------------------------+  |
|  | Causal Jump Tracker| -> | Route Calculator    | -> | Metrics Projection     |  |
|  +--------------------+    +---------------------+    +------------------------+  |
|                                                                    |              |
|                                                                    v              |
|                                                         [NavigationProgressDTO]   |
+-----------------------------------------------------------------------------------+
```

### 1.1 In-Scope
* Tracking multi-jump journey progress using active `NavRoute` data and observed `FSDJump` transitions.
* Calculating estimated time of arrival (ETA) based on empirical hyperspace jump intervals ($\sim 32\text{ seconds}$ per jump cycle).
* Calculating real-time orbital velocities, atmospheric entry glide vectors, and celestial body distances.

### 1.2 Out-of-Scope
* Plotting routes across the galaxy (owned by Frontier's game engine).

---

## 2. Actors and Stakeholders

* **Primary Actor:** Consumer Application.
* **Stakeholder (Developer):** Requires pre-calculated navigation and flight physics metrics without implementing complex mathematical physics formulas.

---

## 3. Pre-conditions and Post-conditions

### 3.1 Pre-conditions
1. `EliteDangerousClient` has an active telemetry stream.
2. A navigation route has been plotted (generating a `NavRoute` snapshot).

### 3.2 Post-conditions
1. **Success:** Returns precise remaining jump counts, elapsed travel time, and accurate arrival ETAs.
2. **Failure:** If no route is currently plotted, returns a clean null state without throwing exceptions.

---

## 4. Main Success Scenario (Basic Flow)

1. The consumer queries current route metrics: `client.navigation.get_route_progress()`.
2. The service inspects the stored `NavRoute` and the current `StarSystem` from `FleetState`.
3. The service calculates remaining jumps and estimates remaining travel duration based on empirical jump cycle timings.
4. The consumer receives the strongly typed progress metrics.

---

## 5. Extensions (Alternative Flows)

* **2a. Ship Strays from Plotted Route:**
  1. The ship jumps to a star system not listed in the current `NavRoute`.
  2. The service flags route status as `OFF_ROUTE`.
  3. Returns a notification recommending recalculation in the Galaxy Map.
