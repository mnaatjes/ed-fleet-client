---
title: "Getting Started with ed-fleet-client"
tags: ["tutorial", "getting-started", "facade", "events", "state"]
created_at: "2026-11-15"
last_updated_at: "2026-11-15"
---

# Getting Started with ed-fleet-client

This tutorial walks you through starting a new Python project, connecting to an `ed-telemetry` API instance, listening for live game events, and reading reduced ship and location state.

---

## 1. Start Your Project

Create a new Python project and install `ed-fleet-client`:

```bash
uv init my-ed-app
cd my-ed-app
uv add ed-fleet-client
```

---

## 2. Ensure `ed-telemetry` Is Running

`ed-fleet-client` connects over HTTP/SSE to an independently running `ed-telemetry` server. Start `ed-telemetry` on your host (default `http://127.0.0.1:8080`) and verify it is reachable:

```bash
curl http://127.0.0.1:8080/api/v1/state
```

---

## 3. Connect, Listen for Events, and Read State

Create `main.py` using `create_client()` and `async with`:

```python
import asyncio
from ed_models import JournalEvent
from ed_fleet_client import create_client
from ed_fleet_client.adapters.driven.telemetry_http import TelemetryConnectionConfig


async def main() -> None:
    config = TelemetryConnectionConfig(host="127.0.0.1", port=8080)
    async with create_client(config) as client:
        @client.on(JournalEvent)
        def on_journal_event(event: JournalEvent) -> None:
            print(f"Event received: {event.event}")
            print(f"Current system: {client.location.star_system}")
            print(f"Fuel main: {client.ship.fuel_main}")

        await asyncio.sleep(30)


if __name__ == "__main__":
    asyncio.run(main())
```

Run your script:

```bash
uv run python main.py
```
