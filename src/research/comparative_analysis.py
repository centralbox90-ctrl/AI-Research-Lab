from __future__ import annotations

from dataclasses import dataclass

from src.research.event_study_result import (
    EventStudyResult,
)
from src.research.horizon_comparison import (
    HorizonComparison,
)
from src.research.horizon_statistics import (
    HorizonStatistics,
)


@dataclass(frozen=True, slots=True)
class ComparativeAnalysis:
    """
    Candidate and baseline results with aligned comparisons.
    """

    candidate_result: EventStudyResult
    baseline_result: EventStudyResult
    candidate_statistics: tuple[
        HorizonStatistics,
        ...,
    ]
    baseline_statistics: tuple[
        HorizonStatistics,
        ...,
    ]
    comparisons: tuple[
        HorizonComparison,
        ...,
    ]

    def __post_init__(self) -> None:
        if not isinstance(
            self.candidate_result,
            EventStudyResult,
        ):
            raise TypeError(
                "candidate_result must be an "
                "EventStudyResult"
            )

        if not isinstance(
            self.baseline_result,
            EventStudyResult,
        ):
            raise TypeError(
                "baseline_result must be an "
                "EventStudyResult"
            )

        if (
            self.candidate_result.specification
            != self.baseline_result.specification
        ):
            raise ValueError(
                "candidate and baseline must use "
                "the same specification"
            )

        if not self.candidate_result.observation_ids:
            raise ValueError(
                "candidate_result must contain "
                "complete observations"
            )

        if not self.baseline_result.observation_ids:
            raise ValueError(
                "baseline_result must contain "
                "complete observations"
            )

        candidate_by_horizon = (
            self._index_values(
                self.candidate_statistics,
                field_name="candidate_statistics",
                expected_type=HorizonStatistics,
            )
        )
        baseline_by_horizon = (
            self._index_values(
                self.baseline_statistics,
                field_name="baseline_statistics",
                expected_type=HorizonStatistics,
            )
        )
        comparison_by_horizon = (
            self._index_values(
                self.comparisons,
                field_name="comparisons",
                expected_type=HorizonComparison,
            )
        )

        expected_horizons = set(
            self.candidate_result
            .specification
            .horizons
        )

        if set(candidate_by_horizon) != expected_horizons:
            raise ValueError(
                "candidate_statistics must cover "
                "all requested horizons"
            )

        if set(baseline_by_horizon) != expected_horizons:
            raise ValueError(
                "baseline_statistics must cover "
                "all requested horizons"
            )

        if set(comparison_by_horizon) != expected_horizons:
            raise ValueError(
                "comparisons must cover all "
                "requested horizons"
            )

        for horizon in expected_horizons:
            candidate = candidate_by_horizon[horizon]
            baseline = baseline_by_horizon[horizon]
            comparison = comparison_by_horizon[
                horizon
            ]

            if (
                candidate.sample_size
                != self.candidate_result
                .observation_count
            ):
                raise ValueError(
                    "candidate sample size must match "
                    "candidate observation count"
                )

            if (
                baseline.sample_size
                != self.baseline_result
                .observation_count
            ):
                raise ValueError(
                    "baseline sample size must match "
                    "baseline observation count"
                )

            if (
                comparison.candidate_sample_size
                != candidate.sample_size
                or comparison.baseline_sample_size
                != baseline.sample_size
            ):
                raise ValueError(
                    "comparison sample sizes must match "
                    "the analyzed statistics"
                )

    @staticmethod
    def _index_values(
        values: object,
        *,
        field_name: str,
        expected_type: type,
    ) -> dict[int, object]:
        if not isinstance(values, tuple):
            raise TypeError(
                f"{field_name} must be a tuple"
            )

        indexed: dict[int, object] = {}

        for value in values:
            if not isinstance(
                value,
                expected_type,
            ):
                raise TypeError(
                    f"each {field_name} value must be "
                    f"{expected_type.__name__}"
                )

            if value.horizon in indexed:
                raise ValueError(
                    f"{field_name} must not contain "
                    "duplicate horizons"
                )

            indexed[value.horizon] = value

        return indexed
