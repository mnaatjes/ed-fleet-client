---
title: "Use-Case Specification: UC-02 Dispatch Domain Events to Observers"
use_case_id: "UC-02"
status: "approved"
version: "1.0.0"
level: "sea_level"
primary_actor: "Consumer Application"
created_at: "2026-11-13"
last_updated_at: "2026-11-13"
tags: ["use-case", "requirements", "dispatcher", "events", "observer", "pubsub"]
---

# Use-Case Specification: UC-02 Dispatch Domain Events to Observers

## 1. System Boundary and Scope

```text
+-----------------------------------------------------------------------------------+
| System Boundary: ed-fleet-client (Event Dispatcher Core)                          |
|                                                                                   |
|  [Actor: Consumer Application]                                                    |
|       |                                                                           |
|       | 1. client.on_event(EventType, handler)                                    |
|       v                                                                           |
|  +--------------------+    +---------------------+    +------------------------+  |
|  | Observer Registry  | -> | Type-Safe Router    | -> | Asynchronous Dispatch  |  |
|  +--------------------+    +---------------------+    +------------------------+  |
|                                                                    |              |
|                                                                    v              |
|                                                         [User Callback Invoked]   |
+-----------------------------------------------------------------------------------+
```

### 1.1 In-Scope
* Registering strongly typed callback functions for concrete `ed-models` domain events (e.g., `FSDJump`, `Docked`, `MarketBuy`).
* Routing deserialized domain events to all matching observers.
* Providing high-level composite lifecycle subscriptions (e.g. `hyperspace_transit`, `station_docking`).
* Isolating subscriber exceptions so failure in one callback does not break other observers.

### 1.2 Out-of-Scope
* Parsing raw log strings (owned by `adapters/driving/hydrator/`).
* Persistent queuing across restarts (in-memory pub/sub only).

---

## 2. Actors and Stakeholders

* **Primary Actor:** Consumer Application.
* **Stakeholder (Developer):** Requires type-hinted, zero-boilerplate event subscriptions that execute reliably without crashing the main application loop.

---

## 3. Pre-conditions and Post-conditions

### 3.1 Pre-conditions
1. `EliteDangerousClient` is running.
2. The consumer provides a callable handler accepting a specific typed event parameter.

### 3.2 Post-conditions
1. **Success:** The handler is executed whenever an event of that type occurs, receiving the strongly typed model instance.
2. **Failure:** If a handler throws an unhandled exception, the dispatcher captures the error, logs a diagnostic warning, and proceeds to remaining observers.

---

## 4. Main Success Scenario (Basic Flow)

1. The consumer subscribes to an event type: `client.on_event(FSDJump, on_jump)`.
2. The client receives and hydrator parses an incoming `FSDJump` log record.
3. The event router matches the event against active subscriptions in the Observer Registry.
4. The router dispatches the typed event to `on_jump(event)`.
5. The consumer callback processes the event and completes.

---

## 5. Extensions (Alternative Flows)

* **4a. Handler Throws Unhandled Exception:**
  1. The user's callback raises an unexpected exception.
  2. The dispatcher isolates the error, preventing the ingestion thread from crashing.
  3. The error is logged to the client's diagnostic logger with a full stack trace.
  4. Remaining registered observers receive the event uninterrupted.
