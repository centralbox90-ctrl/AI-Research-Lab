from __future__ import annotations

from dataclasses import dataclass
from math import isclose

from src.application.market_dataset_quality import (
    DataQualityReport,
)
from src.research.comparative_analysis import (
    ComparativeAnalysis,
)
from src.research.comparative_statistical_evaluation import (
    ComparativeStatisticalEvaluation,
)
from src.research.market_dataset_fingerprint import (
    MarketDatasetFingerprint,
)
from src.research.specification import (
    ResearchSpecification,
)


@dataclass(frozen=True, slots=True)
class IndicatorComparativeResearchResult:
    """Reproducible result of comparative indicator research."""

    indicator_id: str
    symbol: str
    timeframe: str
    research_specification: ResearchSpecification
    dataset_fingerprint: MarketDatasetFingerprint
    data_quality_report: DataQualityReport
    analysis: ComparativeAnalysis
    statistical_evaluations: tuple[
        ComparativeStatisticalEvaluation,
        ...,
    ] = ()

    def __post_init__(self) -> None:
        indicator_id = self._normalize_text(
            self.indicator_id,
            field_name="indicator_id",
        )
        symbol = self._normalize_text(
            self.symbol,
            field_name="symbol",
            uppercase=True,
        )
        timeframe = self._normalize_text(
            self.timeframe,
            field_name="timeframe",
            uppercase=True,
        )

        if not isinstance(
            self.research_specification,
            ResearchSpecification,
        ):
            raise TypeError(
                "research_specification must be a "
                "ResearchSpecification"
            )

        if (
            self.research_specification
            .indicator
            .indicator_id
            != indicator_id
        ):
            raise ValueError(
                "indicator_id must match the "
                "research specification"
            )

        if not isinstance(
            self.dataset_fingerprint,
            MarketDatasetFingerprint,
        ):
            raise TypeError(
                "dataset_fingerprint must be a "
                "MarketDatasetFingerprint"
            )

        if not isinstance(
            self.data_quality_report,
            DataQualityReport,
        ):
            raise TypeError(
                "data_quality_report must be a "
                "DataQualityReport"
            )

        if not isinstance(
            self.analysis,
            ComparativeAnalysis,
        ):
            raise TypeError(
                "analysis must be a ComparativeAnalysis"
            )

        statistical_evaluations = (
            self._validate_statistical_evaluations()
        )

        object.__setattr__(
            self,
            "indicator_id",
            indicator_id,
        )
        object.__setattr__(
            self,
            "symbol",
            symbol,
        )
        object.__setattr__(
            self,
            "timeframe",
            timeframe,
        )
        object.__setattr__(
            self,
            "statistical_evaluations",
            statistical_evaluations,
        )

    def _validate_statistical_evaluations(
        self,
    ) -> tuple[
        ComparativeStatisticalEvaluation,
        ...,
    ]:
        evaluations = self.statistical_evaluations

        if not isinstance(evaluations, tuple):
            raise TypeError(
                "statistical_evaluations must be a tuple"
            )

        if not evaluations:
            return ()

        evaluation_by_horizon: dict[
            int,
            ComparativeStatisticalEvaluation,
        ] = {}

        for evaluation in evaluations:
            if not isinstance(
                evaluation,
                ComparativeStatisticalEvaluation,
            ):
                raise TypeError(
                    "each statistical evaluation must be a "
                    "ComparativeStatisticalEvaluation"
                )

            if evaluation.horizon in evaluation_by_horizon:
                raise ValueError(
                    "statistical evaluations must not "
                    "contain duplicate horizons"
                )

            evaluation_by_horizon[
                evaluation.horizon
            ] = evaluation

        comparison_by_horizon = {
            comparison.horizon: comparison
            for comparison in self.analysis.comparisons
        }

        if set(evaluation_by_horizon) != set(
            comparison_by_horizon
        ):
            raise ValueError(
                "statistical evaluations must cover "
                "all comparison horizons"
            )

        expected_research_fingerprint = (
            self.research_specification.fingerprint
        )
        expected_dataset_id = (
            self.dataset_fingerprint
            .dataset_fingerprint
        )

        for (
            horizon,
            evaluation,
        ) in evaluation_by_horizon.items():
            comparison = comparison_by_horizon[
                horizon
            ]

            if (
                evaluation.research_fingerprint
                != expected_research_fingerprint
            ):
                raise ValueError(
                    "statistical evaluation research "
                    "fingerprint must match the result"
                )

            if (
                evaluation.dataset_id
                != expected_dataset_id
            ):
                raise ValueError(
                    "statistical evaluation dataset id "
                    "must match the result"
                )

            if (
                evaluation.candidate_sample_size
                != comparison.candidate_sample_size
            ):
                raise ValueError(
                    "statistical evaluation candidate "
                    "sample size must match the comparison"
                )

            if (
                evaluation.baseline_sample_size
                != comparison.baseline_sample_size
            ):
                raise ValueError(
                    "statistical evaluation baseline "
                    "sample size must match the comparison"
                )

            if not isclose(
                evaluation.effect_estimate,
                comparison.mean_return_difference,
                rel_tol=1e-12,
                abs_tol=1e-15,
            ):
                raise ValueError(
                    "statistical evaluation effect estimate "
                    "must match the comparison"
                )

        return tuple(
            evaluation_by_horizon[horizon]
            for horizon in sorted(
                evaluation_by_horizon
            )
        )

    @property
    def research_fingerprint(self) -> str:
        return self.research_specification.fingerprint

    @property
    def dataset_id(self) -> str:
        return (
            self.dataset_fingerprint
            .dataset_fingerprint
        )

    @staticmethod
    def _normalize_text(
        value: object,
        *,
        field_name: str,
        uppercase: bool = False,
    ) -> str:
        if not isinstance(value, str):
            raise TypeError(
                f"{field_name} must be a string"
            )

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                f"{field_name} must not be empty"
            )

        if uppercase:
            return normalized.upper()

        return normalized
