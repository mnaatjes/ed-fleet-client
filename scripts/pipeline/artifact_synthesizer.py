"""Artifact synthesizer rendering JSON, Engineering Markdown, and Diataxis Reference."""

import json
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from scripts.pipeline.corpus_miner import EventCadenceMetrics
from scripts.pipeline.fidelity_scorer import ScoredPropertyDimension
from scripts.pipeline.schema_inspector import EventSchemaMeta, discover_projection_targets

PROJECTION_TARGET_MAP: dict[str, str] = discover_projection_targets()


class ArtifactSynthesizer:
    """Renders data and documentation artifacts across Engineering and Developer planes."""

    def __init__(
        self,
        ed_models_version: str,
        schemas: dict[str, EventSchemaMeta],
        cadence_metrics: dict[str, EventCadenceMetrics],
        scored_dimensions: dict[str, ScoredPropertyDimension],
    ) -> None:
        self.version = ed_models_version
        self.schemas = schemas
        self.cadence = cadence_metrics
        self.dimensions = scored_dimensions

    def render_json_matrix(self, output_path: Path | str) -> None:
        """Render machine-readable traversible JSON graph."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        matrix_data: dict[str, Any] = {
            "version": self.version,
            "generated_at": datetime.now(UTC).isoformat(),
            "properties_count": len(self.dimensions),
            "events_count": len(self.schemas),
            "properties": {},
        }

        for prop_name, dim in sorted(self.dimensions.items()):
            matrix_data["properties"][prop_name] = {
                "property_name": dim.property_name,
                "tier": dim.tier,
                "primary_event": dim.primary_event,
                "primary_score": dim.primary_score,
                "projection_path": PROJECTION_TARGET_MAP.get(prop_name, "unmapped"),
                "fallback_events": dim.fallback_events,
                "sources": [asdict(s) for s in dim.all_scores],
            }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(matrix_data, f, indent=2)

    def render_engineering_markdown(self, output_path: Path | str) -> None:
        """Render Engineering Plane Markdown table matrix."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        lines: list[str] = [
            "---",
            'title: "Property Fidelity & Event Mapping Matrix"',
            'tags: ["architecture", "telemetry", "fidelity", "matrix", "reference"]',
            f'created_at: "{datetime.now(UTC).strftime("%Y-%m-%d")}"',
            f'last_updated_at: "{datetime.now(UTC).strftime("%Y-%m-%d")}"',
            "---",
            "",
            "# Property Fidelity & Event Mapping Matrix",
            "",
            (
                f"Generated from **`ed-models` v{self.version}** via "
                "`scripts/map_property_event_matrix.py`."
            ),
            "",
            "## 1. Executive Summary & Dimension Overview",
            "",
            f"- **Target Model Version:** `v{self.version}`",
            f"- **Canonical Properties Analyzed:** {len(self.dimensions)}",
            f"- **Journal & Telemetry Schemas Reflected:** {len(self.schemas)}",
            "",
            "## 2. Tier 1 & Tier 2 Canonical Navigation and Vessel State",
            "",
            (
                "| Canonical Property | Tier | Primary Source | Score | "
                "Projection Target | Fallback Sources |"
            ),
            "| :--- | :---: | :--- | :---: | :--- | :--- |",
        ]

        tier_1_2 = sorted(
            [d for d in self.dimensions.values() if d.tier in (1, 2)],
            key=lambda x: (x.tier, x.property_name),
        )

        for d in tier_1_2:
            proj = PROJECTION_TARGET_MAP.get(d.property_name, "*none*")
            fallbacks = ", ".join(d.fallback_events[:3]) if d.fallback_events else "*none*"
            lines.append(
                f"| `{d.property_name}` | {d.tier} | `{d.primary_event}` | "
                f"{d.primary_score:.2f} | `{proj}` | {fallbacks} |"
            )

        lines.extend(
            [
                "",
                "## 3. Tier 3 Contextual & Market State",
                "",
                (
                    "| Canonical Property | Tier | Primary Source | Score | "
                    "Projection Target | Fallback Sources |"
                ),
                "| :--- | :---: | :--- | :---: | :--- | :--- |",
            ]
        )

        tier_3 = sorted(
            [d for d in self.dimensions.values() if d.tier == 3],
            key=lambda x: x.property_name,
        )

        for d in tier_3:
            proj = PROJECTION_TARGET_MAP.get(d.property_name, "*none*")
            fallbacks = ", ".join(d.fallback_events[:3]) if d.fallback_events else "*none*"
            lines.append(
                f"| `{d.property_name}` | {d.tier} | `{d.primary_event}` | "
                f"{d.primary_score:.2f} | `{proj}` | {fallbacks} |"
            )

        lines.extend(
            [
                "",
                "## 4. Multi-Source Concurrency & Reducer Coverage",
                "",
                "| Property | Concurrency Count | Primary Reducer Target | Reducer Status |",
                "| :--- | :---: | :--- | :---: |",
            ]
        )

        for d in tier_1_2:
            proj = PROJECTION_TARGET_MAP.get(d.property_name)
            status = "**Covered**" if proj else "*Gapped*"
            target = f"`{proj}`" if proj else "*Unassigned*"
            lines.append(
                f"| `{d.property_name}` | {len(d.all_scores)} events | {target} | {status} |"
            )

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

    def render_diataxis_reference(self, output_path: Path | str) -> None:
        """Render Diataxis Reference Guide."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        lines: list[str] = [
            "---",
            'title: "Canonical Property-to-Event Reference Guide"',
            'tags: ["docs", "reference", "telemetry", "events", "properties", "projections"]',
            f'created_at: "{datetime.now(UTC).strftime("%Y-%m-%d")}"',
            f'last_updated_at: "{datetime.now(UTC).strftime("%Y-%m-%d")}"',
            "---",
            "",
            "# Canonical Property-to-Event Reference Guide",
            "",
            (
                "This guide answers the developer question: "
                "***If I need property X, which projection holds it, "
                "and which journal/status events contribute to it?***"
            ),
            "",
            (
                f"> [!NOTE]\n> Pinned to upstream **`ed-models` v{self.version}**. "
                "Generated deterministically by the telemetry pipeline."
            ),
            "",
            "## 1. Quick Property Lookup",
            "",
            (
                "| Desired Property | Target Projection Path | Authoritative Primary Event | "
                "Fallback / Pre-Transition Events |"
            ),
            "| :--- | :--- | :--- | :--- |",
        ]

        important_props = sorted(
            [d for d in self.dimensions.values() if d.tier in (1, 2, 3)],
            key=lambda x: (x.tier, x.property_name),
        )

        for d in important_props:
            raw_proj = PROJECTION_TARGET_MAP.get(d.property_name)
            proj_str = f"`client.state.{raw_proj}`" if raw_proj else "*unmapped*"
            fallbacks = (
                ", ".join(f"`{e}`" for e in d.fallback_events[:3])
                if d.fallback_events
                else "*none*"
            )
            lines.append(
                f"| **`{d.property_name}`** | {proj_str} | `{d.primary_event}` | {fallbacks} |"
            )

        lines.extend(
            [
                "",
                "## 2. Event Sourcing Behavior",
                "",
                "### Spatial & Navigation Properties",
                (
                    "- **`star_system` & `system_address`:** Primary authority is `FSDJump` upon "
                    "hyperspace arrival. If reconnecting during an active session, `Location` "
                    "hydrates initial coordinates. Transitional target is exposed early by "
                    "`FSDTarget` / `StartJump`."
                ),
                (
                    "- **`body_name` & `body_id`:** Updated upon `ApproachBody`, `Touchdown`, "
                    "or orbital telemetry transition."
                ),
                "",
                "### Vessel Loadout & Operations",
                (
                    "- **`ship_model`, `ship_name`, `ship_id`:** Hydrated authoritatively by "
                    "`Loadout` and `ShipyardSwap`."
                ),
                (
                    "- **`fuel_main` & `fuel_reservoir`:** Live streaming updates originate from "
                    "continuous `StatusTelemetry`. Authoritative absolute snapshots arrive on "
                    "`FuelScoop` and `RefuelAll`."
                ),
                "",
                "### Commander & Economy",
                (
                    "- **`cmdr_name` & `cmdr_fid`:** Populated on `Commander` and `LoadGame` "
                    "startup events."
                ),
                (
                    "- **`credits`:** Reflected on startup (`LoadGame`) and updated "
                    "incrementally on transaction events (`MarketBuy`, `MarketSell`, "
                    "`PayFines`, `RedeemVoucher`)."
                ),
            ]
        )

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
