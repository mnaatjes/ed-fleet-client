"""Unit tests for TelemetryHttpClient driven adapter."""

from __future__ import annotations

from ed_fleet_client.adapters.driven.telemetry_http import (
    TelemetryConnectionConfig,
    TelemetryPlane,
    TelemetrySource,
)


def test_connection_config_builds_urls() -> None:
    cfg = TelemetryConnectionConfig(host="127.0.0.1", port=9000)
    assert cfg.base_url == "http://127.0.0.1:9000"
    assert cfg.build_url("/api/v1/status") == "http://127.0.0.1:9000/api/v1/status"


def test_telemetry_enums_from_header() -> None:
    assert TelemetryPlane.from_header("state") == TelemetryPlane.STATE
    assert TelemetryPlane.from_header("unknown-value") == TelemetryPlane.UNKNOWN
    assert TelemetrySource.from_header("memory-buffer") == TelemetrySource.MEMORY_BUFFER
    assert TelemetrySource.from_header(None) == TelemetrySource.UNKNOWN
