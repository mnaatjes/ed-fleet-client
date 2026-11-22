"""Fidelity scoring engine implementing ADR 0005 multi-vector equation."""

from dataclasses import dataclass

from scripts.pipeline.corpus_miner import EventCadenceMetrics
from scripts.pipeline.schema_inspector import EventSchemaMeta


@dataclass(frozen=True)
class PropertySourceScore:
    """Scoring breakdown for a specific (property, event) source."""

    property_name: str
    event_name: str
    completeness: float  # C: 0.0 - 1.0
    uniqueness: float  # U: 0.0 - 1.0
    phase_accuracy: float  # A: 0.0 - 1.0
    recency: float  # R: 0.0 - 1.0
    composite_score: float  # S_fidelity: 0.0 - 1.0
    rank: int  # 1 = primary source, 2+ = fallback / secondary


@dataclass(frozen=True)
class ScoredPropertyDimension:
    """Consolidated fidelity dimension for a canonical property."""

    property_name: str
    tier: int
    primary_event: str
    primary_score: float
    fallback_events: list[str]
    all_scores: list[PropertySourceScore]


class FidelityScorer:
    """Computes ADR 0005 fidelity scores for all property-to-event relationships."""

    # Weights defined in ADR 0005 Section 4.6
    WEIGHT_COMPLETENESS = 0.35
    WEIGHT_UNIQUENESS = 0.30
    WEIGHT_PHASE_ACCURACY = 0.20
    WEIGHT_RECENCY = 0.15

    def score_source(
        self,
        prop_name: str,
        event_meta: EventSchemaMeta,
        field_name: str,
        cadence: EventCadenceMetrics,
    ) -> PropertySourceScore:
        """Compute fidelity score vectors for a single event-property pair."""
        field_meta = event_meta.fields[field_name]

        # 1. Completeness (C)
        if field_meta.is_optional:
            c = 0.5
        else:
            c = 1.0

        # 2. Uniqueness (U)
        if field_meta.is_authoritative_id:
            u = 1.0
        elif "int" in field_meta.field_type or "float" in field_meta.field_type:
            u = 0.9
        elif "str" in field_meta.field_type:
            u = 0.7
        else:
            u = 0.6

        # 3. Phase Accuracy (A)
        # Post-transition events (e.g. FSDJump, Location, Docked) have high accuracy (1.0).
        # StatusTelemetry is instantaneous (1.0).
        # Transitional events (StartJump, FSDTarget) have intent-phase accuracy (0.5).
        ev_name = event_meta.event_name
        if "Start" in ev_name or "Target" in ev_name or "Request" in ev_name:
            a = 0.5
        elif event_meta.is_status:
            a = 1.0
        else:
            a = 1.0

        # 4. Recency (R)
        # Based on cadence / inter-arrival latency
        if cadence.cadence_type == "continuous_poll":
            r = 1.0
        elif cadence.cadence_type == "regime_phase":
            r = 0.7
        else:
            r = 0.4

        # Composite S_fidelity = 0.35*C + 0.30*U + 0.20*A + 0.15*R
        score = (
            self.WEIGHT_COMPLETENESS * c
            + self.WEIGHT_UNIQUENESS * u
            + self.WEIGHT_PHASE_ACCURACY * a
            + self.WEIGHT_RECENCY * r
        )
        score = round(score, 4)

        return PropertySourceScore(
            property_name=prop_name,
            event_name=ev_name,
            completeness=c,
            uniqueness=u,
            phase_accuracy=a,
            recency=r,
            composite_score=score,
            rank=0,  # Assigned after sorting
        )

    def score_all_properties(
        self,
        schema_metas: dict[str, EventSchemaMeta],
        property_to_events: dict[str, list[str]],
        cadence_metrics: dict[str, EventCadenceMetrics],
        property_tiers: dict[str, int],
    ) -> dict[str, ScoredPropertyDimension]:
        """Score and rank all sources for each property."""
        scored_dimensions: dict[str, ScoredPropertyDimension] = {}

        for prop_name, event_names in property_to_events.items():
            tier = property_tiers.get(prop_name, 4)
            source_scores: list[PropertySourceScore] = []

            for ev_name in event_names:
                ev_meta = schema_metas.get(ev_name)
                if not ev_meta:
                    continue

                # Find which field matches this property
                matching_fields = [
                    f_name
                    for f_name, f_meta in ev_meta.fields.items()
                    if f_meta.canonical_property == prop_name
                ]
                if not matching_fields:
                    continue

                cadence = cadence_metrics.get(
                    ev_name,
                    EventCadenceMetrics(
                        event_name=ev_name,
                        lambda_per_hour=0.5,
                        median_delta_seconds=7200.0,
                        cadence_type="rare_lifecycle",
                    ),
                )

                # Score using the highest scoring field if multiple match
                best_field = matching_fields[0]
                sc = self.score_source(prop_name, ev_meta, best_field, cadence)
                source_scores.append(sc)

            # Sort descending by score; prioritize post-transition journal events over Status
            source_scores.sort(
                key=lambda s: (s.composite_score, 0 if s.event_name.startswith("Status") else 1),
                reverse=True,
            )

            # Assign ranks
            ranked_scores: list[PropertySourceScore] = []
            for rank_idx, s in enumerate(source_scores, start=1):
                ranked_scores.append(
                    PropertySourceScore(
                        property_name=s.property_name,
                        event_name=s.event_name,
                        completeness=s.completeness,
                        uniqueness=s.uniqueness,
                        phase_accuracy=s.phase_accuracy,
                        recency=s.recency,
                        composite_score=s.composite_score,
                        rank=rank_idx,
                    )
                )

            if ranked_scores:
                primary = ranked_scores[0]
                fallbacks = [s.event_name for s in ranked_scores[1:]]
                scored_dimensions[prop_name] = ScoredPropertyDimension(
                    property_name=prop_name,
                    tier=tier,
                    primary_event=primary.event_name,
                    primary_score=primary.composite_score,
                    fallback_events=fallbacks,
                    all_scores=ranked_scores,
                )

        return scored_dimensions
