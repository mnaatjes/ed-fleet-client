#!/usr/bin/env python3
"""CLI Entrypoint for the Deterministic Telemetry Property-to-Event Mapping Pipeline.

Governed by ADR 0005 and SDD 0006.
"""

import argparse
import sys
from pathlib import Path

# Ensure repository root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.pipeline.artifact_synthesizer import ArtifactSynthesizer  # noqa: E402
from scripts.pipeline.corpus_miner import CorpusMiner  # noqa: E402
from scripts.pipeline.fidelity_scorer import FidelityScorer  # noqa: E402
from scripts.pipeline.schema_inspector import SchemaInspector  # noqa: E402
from scripts.pipeline.version_validator import VersionValidator  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run deterministic telemetry property-to-event derivation and fidelity pipeline."
        )
    )
    parser.add_argument(
        "--pyproject",
        default=str(REPO_ROOT / "pyproject.toml"),
        help="Path to pyproject.toml",
    )
    parser.add_argument(
        "--corpus-dir",
        default=None,
        help="Optional path to journal logs corpus",
    )
    parser.add_argument(
        "--out-json",
        default=None,
        help="Custom output path for JSON matrix",
    )
    parser.add_argument(
        "--out-arch",
        default=str(REPO_ROOT / "architecture" / "reference" / "property_fidelity_matrix.md"),
        help="Custom output path for engineering markdown matrix",
    )
    parser.add_argument(
        "--out-docs",
        default=str(REPO_ROOT / "docs" / "reference" / "canonical_property_map.md"),
        help="Custom output path for Diataxis reference guide",
    )
    parser.add_argument(
        "--out-reducers",
        default=str(REPO_ROOT / "docs" / "reference" / "state_projections_and_reducers.md"),
        help="Custom output path for Diataxis state projections and reducers manual",
    )
    parser.add_argument(
        "--out-unmapped",
        default=str(REPO_ROOT / "docs" / "reference" / "event_streaming_catalog.md"),
        help="Custom output path for Diataxis event-only streaming catalog",
    )
    parser.add_argument(
        "--skip-version-check",
        action="store_true",
        help="Bypass strict version validation between pyproject.toml and ed-models",
    )

    args = parser.parse_args()

    # Step 1: Version Validation
    validator = VersionValidator(args.pyproject)
    val_result = validator.validate()
    print(f"[1/5] Validating ed-models version: {val_result.details}")
    if not val_result.is_valid and not args.skip_version_check:
        print(f"ERROR: {val_result.details}", file=sys.stderr)
        return 1

    clean_ver = val_result.installed_version.lstrip("v")
    json_path = (
        Path(args.out_json)
        if args.out_json
        else REPO_ROOT
        / "architecture"
        / "reference"
        / "data"
        / f"property_event_matrix.v{clean_ver}.json"
    )

    # Step 2: AST Schema Inspection
    print("[2/5] Inspecting ed-models AST schemas and dataclass fields...")
    inspector = SchemaInspector()
    schemas = inspector.discover_all_schemas()
    prop_to_events = inspector.property_to_events
    print(f"      Reflected {len(schemas)} event schemas across {len(prop_to_events)} properties.")

    # Step 3: Empirical Corpus Mining
    print("[3/5] Mining cadence and concurrency metrics...")
    miner = CorpusMiner(args.corpus_dir)
    cadence = miner.calculate_event_metrics(list(schemas.keys()))
    concurrency = miner.compute_concurrency_overlap(prop_to_events)
    print(
        f"      Computed cadence metrics for {len(cadence)} events "
        f"and {len(concurrency)} property overlaps."
    )

    # Step 4: Multi-Vector Fidelity Scoring
    print(
        "[4/5] Scoring fidelity dimensions (Completeness, Uniqueness, Phase Accuracy, Recency)..."
    )
    from scripts.pipeline.schema_inspector import PROPERTY_TIERS

    scorer = FidelityScorer()
    scored_dims = scorer.score_all_properties(
        schema_metas=schemas,
        property_to_events=prop_to_events,
        cadence_metrics=cadence,
        property_tiers=PROPERTY_TIERS,
    )
    print(
        f"      Ranked primary and fallback event sources for {len(scored_dims)} "
        "canonical properties."
    )

    # Step 5: Dual-Plane Artifact Synthesis
    print("[5/5] Synthesizing output artifacts...")
    synthesizer = ArtifactSynthesizer(
        ed_models_version=clean_ver,
        schemas=schemas,
        cadence_metrics=cadence,
        scored_dimensions=scored_dims,
    )

    # 5a. JSON Graph
    synthesizer.render_json_matrix(json_path)
    print(f"      - JSON Graph: {json_path}")

    # 5b. Engineering Markdown Matrix
    arch_path = Path(args.out_arch)
    synthesizer.render_engineering_markdown(arch_path)
    print(f"      - Engineering Markdown: {arch_path}")

    # 5c. Diataxis Reference Guide
    docs_path = Path(args.out_docs)
    synthesizer.render_diataxis_reference(docs_path)
    print(f"      - Diataxis Reference: {docs_path}")

    # 5d. Diataxis Reducer Reference Manual
    reducers_path = Path(args.out_reducers)
    synthesizer.render_reducer_reference(reducers_path)
    print(f"      - Reducer Reference:  {reducers_path}")

    # 5e. Diataxis Event-Only Streaming Catalog
    unmapped_path = Path(args.out_unmapped)
    synthesizer.render_unmapped_catalog(unmapped_path)
    print(f"      - Event Catalog:      {unmapped_path}")

    print("\nPipeline execution complete. All artifacts generated deterministically.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
