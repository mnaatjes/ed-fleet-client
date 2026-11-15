"""Middleware capturing and hydrating response metadata from ed-telemetry endpoints."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from ed_transport.core.ports.dto import HttpResponseDTO

from .models import (
    EndpointMetadata,
    TelemetryPlane,
    TelemetryResponse,
    TelemetrySource,
)


class MetadataHydrationMiddleware:
    """Extracts endpoint metadata headers, deserializes raw payloads, and builds unified DTOs."""

    @staticmethod
    def _find_header(headers: Mapping[str, str], target_key: str) -> str | None:
        """Case-insensitive header lookup."""
        target_lower = target_key.lower()
        for k, v in headers.items():
            if k.lower() == target_lower:
                return v
        return None

    def hydrate(
        self,
        endpoint_url: str,
        response: HttpResponseDTO,
        latency_ms: float = 0.0,
    ) -> TelemetryResponse[Any]:
        """Hydrates response headers into EndpointMetadata and decodes raw JSON payload."""
        headers = response.headers or {}

        plane_hdr = self._find_header(headers, "X-Telemetry-Plane")
        source_hdr = self._find_header(headers, "X-Telemetry-Source")
        etag_hdr = self._find_header(headers, "ETag")
        content_type_hdr = self._find_header(headers, "Content-Type")

        plane = TelemetryPlane.from_header(plane_hdr)
        source = TelemetrySource.from_header(source_hdr)

        metadata = EndpointMetadata(
            endpoint_url=endpoint_url,
            status_code=response.status_code,
            plane=plane,
            source=source,
            etag=etag_hdr,
            content_type=content_type_hdr,
            latency_ms=latency_ms,
            headers=dict(headers),
        )

        raw_payload = response.body
        data: Any = None
        if raw_payload:
            try:
                data = json.loads(raw_payload.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                data = raw_payload.decode("utf-8", errors="replace")

        return TelemetryResponse(
            metadata=metadata,
            raw_payload=raw_payload,
            data=data,
        )
