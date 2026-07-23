from __future__ import annotations

from dataclasses import asdict

from src.application.indicator_comparative_research_result import (
    IndicatorComparativeResearchResult,
)
from src.research.event_study_result import (
    EventStudyResult,
)


def present_indicator_comparative_research_result(
    result: IndicatorComparativeResearchResult,
) -> dict[str, object]:
    """Build a JSON-compatible comparative research payload."""

    if not isinstance(
        result,
        IndicatorComparativeResearchResult,
    ):
        raise TypeError(
            "result must be an "
            "IndicatorComparativeResearchResult"
        )

    analysis = result.analysis
    outcome_specification = (
        analysis.candidate_result.specification
    )

    return {
        "artifact_type": (
            "indicator_comparative_research"
        ),
        "artifact_version": 1,
        "indicator": {
            "id": result.indicator_id,
            "research_fingerprint": (
                result.research_fingerprint
            ),
            "specification": (
                result.research_specification.to_dict()
            ),
        },
        "market": {
            "symbol": result.symbol,
            "timeframe": result.timeframe,
        },
        "dataset": {
            "id": result.dataset_id,
            "fingerprint": asdict(
                result.dataset_fingerprint
            ),
            "quality": asdict(
                result.data_quality_report
            ),
        },
        "evaluation_plan": {
            "fingerprint": (
                result.evaluation_plan_fingerprint
            ),
            "specification": (
                result.evaluation_plan.to_dict()
            ),
        },
        "outcome_specification": {
            "horizons": list(
                outcome_specification.horizons
            ),
            "price_field": (
                outcome_specification.price_field
            ),
        },
        "analysis": {
            "candidate": _present_event_study(
                analysis.candidate_result
            ),
            "baseline": _present_event_study(
                analysis.baseline_result
            ),
            "candidate_statistics": [
                asdict(statistics)
                for statistics in (
                    analysis.candidate_statistics
                )
            ],
            "baseline_statistics": [
                asdict(statistics)
                for statistics in (
                    analysis.baseline_statistics
                )
            ],
            "comparisons": [
                asdict(comparison)
                for comparison in analysis.comparisons
            ],
            "statistical_evaluations": [
                {
                    **asdict(evaluation),
                    "excludes_zero": (
                        evaluation.excludes_zero
                    ),
                }
                for evaluation in (
                    result.statistical_evaluations
                )
            ],
        },
    }


def _present_event_study(
    result: EventStudyResult,
) -> dict[str, object]:
    return {
        "observation_count": (
            result.observation_count
        ),
        "incomplete_observation_count": (
            result.incomplete_observation_count
        ),
        "outcome_count": result.outcome_count,
        "observation_ids": list(
            result.observation_ids
        ),
        "incomplete_observation_ids": list(
            result.incomplete_observation_ids
        ),
        "outcomes": [
            {
                **asdict(outcome),
                "end_bar_index": (
                    outcome.end_bar_index
                ),
                "value": outcome.value,
            }
            for outcome in result.outcomes
        ],
    }
