"""Reusable HTTP client connecting to ed-telemetry endpoints via ed-transport."""

from __future__ import annotations

import time
from collections.abc import AsyncIterator, Mapping
from typing import Any

from ed_transport.adapters.driving.client import TransportClient
from ed_transport.bootstrap.client_factory import create_transport_client

from ....core.ports.driven.telemetry_transport_port import TelemetryTransportPort
from .middleware import MetadataHydrationMiddleware
from .models import TelemetryConnectionConfig, TelemetryResponse


class TelemetryHttpClient(TelemetryTransportPort):
    """HTTP client querying ed-telemetry REST endpoints with metadata hydration."""

    def __init__(
        self,
        config: TelemetryConnectionConfig | None = None,
        *,
        transport_client: TransportClient | None = None,
        middleware: MetadataHydrationMiddleware | None = None,
    ) -> None:
        self.config = config or TelemetryConnectionConfig()
        self._transport_client = transport_client or create_transport_client(
            default_timeout=self.config.timeout
        )
        self._middleware = middleware or MetadataHydrationMiddleware()

    def __enter__(self) -> TelemetryHttpClient:
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    def close(self) -> None:
        """Closes underlying transport resources."""
        self._transport_client.close()

    def _prepare_headers(
        self,
        custom_headers: Mapping[str, str] | None = None,
        if_none_match: str | None = None,
    ) -> dict[str, str]:
        """Prepares request headers injecting API key and ETag cache validators."""
        headers: dict[str, str] = dict(custom_headers) if custom_headers else {}
        if self.config.api_key:
            headers["X-API-Key"] = self.config.api_key
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        if if_none_match:
            headers["If-None-Match"] = if_none_match
        return headers

    def request(
        self,
        path: str | None = None,
        *,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, str] | None = None,
        if_none_match: str | None = None,
        timeout: float | None = None,
    ) -> TelemetryResponse[Any]:
        """Dispatches an HTTP GET request to the target path and returns hydrated DTO."""
        url = self.config.build_url(path)
        req_headers = self._prepare_headers(headers, if_none_match=if_none_match)
        req_timeout = timeout if timeout is not None else self.config.timeout

        start = time.perf_counter()
        http_response = self._transport_client.get(
            url=url,
            headers=req_headers,
            params=params,
            timeout=req_timeout,
        )
        latency_ms = (time.perf_counter() - start) * 1000.0

        return self._middleware.hydrate(
            endpoint_url=url,
            response=http_response,
            latency_ms=latency_ms,
        )

    def get_state(self, if_none_match: str | None = None) -> TelemetryResponse[Any]:
        """Retrieves consolidated state from GET /api/v1/state."""
        return self.request("/api/v1/state", if_none_match=if_none_match)

    def get_state_heartbeat(self, if_none_match: str | None = None) -> TelemetryResponse[Any]:
        """Retrieves lightweight state heartbeat from GET /api/v1/state/heartbeat."""
        return self.request("/api/v1/state/heartbeat", if_none_match=if_none_match)

    def get_status(self) -> TelemetryResponse[Any]:
        """Retrieves cockpit game status from GET /api/v1/status."""
        return self.request("/api/v1/status")

    def get_snapshots(self) -> TelemetryResponse[Any]:
        """Retrieves all registered snapshots map from GET /api/v1/snapshots."""
        return self.request("/api/v1/snapshots")

    async def fetch_status(self) -> dict[str, Any]:
        """Fetches the latest raw Status.json payload via TelemetryTransportPort."""
        resp = self.get_status()
        return dict(resp.data) if isinstance(resp.data, dict) else {}

    async def fetch_snapshot(self, endpoint: str) -> dict[str, Any]:
        """Fetches a raw companion snapshot payload from the given endpoint."""
        resp = self.request(endpoint)
        return dict(resp.data) if isinstance(resp.data, dict) else {}

    async def stream_events(self) -> AsyncIterator[dict[str, Any]]:
        """Streams raw telemetry event payloads."""
        resp = self.get_state()
        if isinstance(resp.data, dict):
            yield dict(resp.data)
