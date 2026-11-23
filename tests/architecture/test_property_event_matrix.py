"""Automated verification tests for the property-event fidelity matrix and pipeline.

Governed by ADR 0005 and SDD 0006.
"""

import json
from pathlib import Path

from scripts.pipeline.corpus_miner import CorpusMiner
from scripts.pipeline.fidelity_scorer import FidelityScorer
from scripts.pipeline.schema_inspector import SchemaInspector
from scripts.pipeline.version_validator import VersionValidator

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def test_version_validator_matches_pyproject() -> None:
    validator = VersionValidator(REPO_ROOT / "pyproject.toml")
    result = validator.validate()
    assert result.is_valid, result.details
    assert result.pinned_rev == "v0.2.1"
    assert result.installed_version == "0.2.1"


def test_schema_inspector_extracts_known_events_and_fields() -> None:
    inspector = SchemaInspector()
    schemas = inspector.discover_all_schemas()

    assert len(schemas) > 200
    assert "FSDJump" in schemas
    assert "StatusTelemetry" in schemas
    assert "Location" in schemas
    assert "Loadout" in schemas

    # Verify field extraction
    fsd_jump = schemas["FSDJump"]
    assert "StarSystem" in fsd_jump.fields or "SystemAddress" in fsd_jump.fields

    # Verify canonical reverse index
    assert "star_system" in inspector.property_to_events
    assert "system_address" in inspector.property_to_events


def test_corpus_miner_computes_cadence_and_overlap() -> None:
    miner = CorpusMiner()
    metrics = miner.calculate_event_metrics(["StatusTelemetry", "FSDJump", "Location"])

    assert metrics["StatusTelemetry"].cadence_type == "continuous_poll"
    assert metrics["StatusTelemetry"].lambda_per_hour >= 3600.0
    assert metrics["FSDJump"].cadence_type == "regime_phase"
    assert metrics["Location"].cadence_type == "rare_lifecycle"

    overlap = miner.compute_concurrency_overlap(
        {"star_system": ["FSDJump", "Location", "ApproachBody"]}
    )
    assert overlap["star_system"]["is_concurrent"] is True
    assert overlap["star_system"]["event_count"] == 3


def test_fidelity_scorer_ranks_authoritative_sources() -> None:
    inspector = SchemaInspector()
    schemas = inspector.discover_all_schemas()
    miner = CorpusMiner()
    cadence = miner.calculate_event_metrics(list(schemas.keys()))

    scorer = FidelityScorer()
    from scripts.pipeline.schema_inspector import PROPERTY_TIERS

    dims = scorer.score_all_properties(
        schema_metas=schemas,
        property_to_events=inspector.property_to_events,
        cadence_metrics=cadence,
        property_tiers=PROPERTY_TIERS,
    )

    assert "star_system" in dims
    assert dims["star_system"].tier == 1
    assert dims["star_system"].primary_score > 0.5
    assert len(dims["star_system"].all_scores) > 1


def test_generated_json_artifact_schema_and_integrity() -> None:
    json_path = (
        REPO_ROOT / "architecture" / "reference" / "data" / "property_event_matrix.v0.2.1.json"
    )
    assert json_path.exists(), f"JSON matrix not found at {json_path}"

    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    assert data["version"] == "0.2.1"
    assert data["properties_count"] > 100
    assert "star_system" in data["properties"]

    star_system_prop = data["properties"]["star_system"]
    assert star_system_prop["tier"] == 1
    assert "primary_event" in star_system_prop
    assert len(star_system_prop["sources"]) > 0


def test_generated_markdown_artifacts_exist_and_conform_to_frontmatter() -> None:
    arch_md = REPO_ROOT / "architecture" / "reference" / "property_fidelity_matrix.md"
    docs_md = REPO_ROOT / "docs" / "reference" / "canonical_property_map.md"
    reducers_md = REPO_ROOT / "docs" / "reference" / "state_projections_and_reducers.md"
    unmapped_md = REPO_ROOT / "docs" / "reference" / "event_streaming_catalog.md"

    for path in (arch_md, docs_md, reducers_md, unmapped_md):
        assert path.exists(), f"Markdown artifact not found: {path}"
        content = path.read_text(encoding="utf-8")
        assert content.startswith("---\n"), f"Missing YAML frontmatter in {path}"
        assert 'title: "' in content
        assert "tags: [" in content
        assert 'created_at: "' in content
        assert 'last_updated_at: "' in content


def test_discover_projection_targets_reflects_domain_models() -> None:
    from scripts.pipeline.schema_inspector import discover_projection_targets

    targets = discover_projection_targets()

    # Verify core domain model fields are automatically discovered
    assert "star_system" in targets
    assert targets["star_system"] == "location.star_system"
    assert "commander_name" in targets
    assert targets["commander_name"] == "session.commander_name"
    assert "ship_type" in targets
    assert targets["ship_type"] == "ship.ship_type"
    assert "ship_id" in targets
    assert targets["ship_id"] == "ship.ship_id"
    assert "hull_health" in targets
    assert targets["hull_health"] == "ship.hull_health"

    # Verify canonical aliases resolve accurately
    assert targets["coordinates"] == "location.star_pos"
    assert targets["body_name"] == "location.body"
    assert targets["pips"] == "ship.telemetry.pips"
    assert targets["flags"] == "ship.telemetry.flags"
    assert targets["fuel_main"] == "ship.telemetry.fuel_main"


def test_inspect_projection_metadata_extracts_all_projections() -> None:
    from scripts.pipeline.schema_inspector import inspect_projection_metadata

    docs = inspect_projection_metadata()
    assert len(docs) == 4

    proj_names = [d.projection_name for d in docs]
    assert "LocationProjection" in proj_names
    assert "SessionProjection" in proj_names
    assert "ShipProjection" in proj_names
    assert "ClientStateProjection" in proj_names

    # Check LocationProjection field count and metadata presence
    loc_doc = next(d for d in docs if d.projection_name == "LocationProjection")
    assert len(loc_doc.fields) >= 15
    field_names = [f.field_name for f in loc_doc.fields]
    assert "star_system" in field_names
    assert "docked" in field_names
    star_system_field = next(f for f in loc_doc.fields if f.field_name == "star_system")
    assert "Authoritative current star system" in star_system_field.description
