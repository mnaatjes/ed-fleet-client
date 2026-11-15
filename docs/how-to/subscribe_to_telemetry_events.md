---
title: "How to Subscribe to Telemetry Events and Read State"
tags: ["how-to", "events", "listeners", "state", "snapshots"]
created_at: "2026-11-15"
last_updated_at: "2026-11-15"
---

# How to Subscribe to Telemetry Events and Read State

`EliteDangerousClient` exposes both decorator-based (`@client.on(...)`) and programmatic (`client.subscribe(...)`) event listeners alongside immutable state projections.

---

## 1. Register Event Listeners

```python
from ed_models import JournalEvent, StatusTelemetry

@client.on(JournalEvent)
def handle_journal(event: JournalEvent) -> None:
    print(event.event, client.location.star_system)

sub = client.subscribe(StatusTelemetry, lambda s: print(s.cargo))
# Later, remove the subscription:
client.unsubscribe(sub)
```

---

## 2. Read Reduced State & Fetch Snapshots

```python
print(client.location.star_system)
print(client.ship.fuel_main)
print(client.session.commander_name)

market = await client.get_snapshot("Market", "/api/v1/snapshots/market")
```
