---
title: "How to Connect to an ed-telemetry API Instance"
tags: ["how-to", "connection", "telemetry", "configuration"]
created_at: "2026-11-15"
last_updated_at: "2026-11-15"
---

# How to Connect to an ed-telemetry API Instance

Use `TelemetryConnectionConfig` to point `EliteDangerousClient` at any local or remote `ed-telemetry` server.

---

## 1. Configure Host, Port, and API Key

```python
from ed_fleet_client import create_client
from ed_fleet_client.adapters.driven.telemetry_http import TelemetryConnectionConfig

config = TelemetryConnectionConfig(
    host="192.168.1.214",
    port=8080,
    api_key="your-api-key-if-enabled",
    timeout=10.0,
)
client = create_client(config)
```

---

## 2. Manage the Connection Lifecycle

Use `async with` for automatic `connect()` and `disconnect()`:

```python
async with create_client(config) as client:
    print("Connected:", client.session.is_live_session)
```
