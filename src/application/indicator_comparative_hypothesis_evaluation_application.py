from __future__ import annotations

from dataclasses import dataclass

from src.application.hypothesis_evaluation_application import (
    HypothesisEvaluationApplication,
)
from src.application.indicator_comparative_finding_application import (
    IndicatorComparativeFindingApplication,
)
from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
)
from src.research.finding_evaluator import (
    FindingEvaluator,
)
from src.research.hypothesis_evaluation import (
    HypothesisEvaluation,
)
from src.research.outcome_specification import (
    ForwardReturnSpecification,
)


@dataclass(frozen=True, slots=True)
class IndicatorComparativeFindingRequest:
    """
    Declarative request for one comparative Finding.
    """

    market_specifications: tuple[
        MarketExperimentSpecification,
        ...,
    ]
    indicator_id: str
    outcome_specification: ForwardReturnSpecification
    horizon: int
    statement: str
    applicable_markets: tuple[str, ...]
    analysis_pipeline_version: str = (
        FindingEvaluator.DEFAULT_PIPELINE_VERSION
    )

    def __post_init__(self) -> None:
        if not isinstance(
            self.market_specifications,
            tuple,
        ):
            raise TypeError(
                "market_specifications must be a tuple"
            )

        if not self.market_specifications:
            raise ValueError(
                "market_specifications must not be empty"
            )

        if any(
            not isinstance(
                specification,
                MarketExperimentSpecification,
            )
            for specification
            in self.market_specifications
        ):
            raise TypeError(
                "each market specification must be a "
                "MarketExperimentSpecification"
            )

        indicator_id = self._normalize_text(
            self.indicator_id,
            field_name="indicator_id",
        )

        if not isinstance(
            self.outcome_specification,
            ForwardReturnSpecification,
        ):
            raise TypeError(
                "outcome_specification must be a "
                "ForwardReturnSpecification"
            )

        if (
            not isinstance(self.horizon, int)
            or isinstance(self.horizon, bool)
        ):
            raise TypeError(
                "horizon must be an integer"
            )

        if (
            self.horizon
            not in self.outcome_specification.horizons
        ):
            raise ValueError(
                "horizon must be declared in "
                "outcome_specification"
            )

        statement = self._normalize_text(
            self.statement,
            field_name="statement",
        )
        applicable_markets = (
            self._normalize_text_items(
                self.applicable_markets,
                field_name="applicable_markets",
            )
        )
        pipeline_version = self._normalize_text(
            self.analysis_pipeline_version,
            field_name=(
                "analysis_pipeline_version"
            ),
        )

        object.__setattr__(
            self,
            "indicator_id",
            indicator_id,
        )
        object.__setattr__(
            self,
            "statement",
            statement,
        )
        object.__setattr__(
            self,
            "applicable_markets",
            applicable_markets,
        )
        object.__setattr__(
            self,
            "analysis_pipeline_version",
            pipeline_version,
        )

    @staticmethod
    def _normalize_text(
        value: object,
        *,
        field_name: str,
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

        return normalized

    @classmethod
    def _normalize_text_items(
        cls,
        value: object,
        *,
        field_name: str,
    ) -> tuple[str, ...]:
        if not isinstance(value, tuple):
            raise TypeError(
                f"{field_name} must be a tuple"
            )

        if not value:
            raise ValueError(
                f"{field_name} must not be empty"
            )

        normalized = tuple(
            cls._normalize_text(
                item,
                field_name=field_name,
            )
            for item in value
        )

        if len(normalized) != len(set(normalized)):
            raise ValueError(
                f"{field_name} must not contain duplicates"
            )

        return tuple(sorted(normalized))


class IndicatorComparativeHypothesisEvaluationApplication:
    """
    Runs comparative research through Findings to hypothesis evaluation.
    """

    def __init__(
        self,
        *,
        finding_application: (
            IndicatorComparativeFindingApplication
        ),
        hypothesis_evaluation_application: (
            HypothesisEvaluationApplication
        ),
    ) -> None:
        if not isinstance(
            finding_application,
            IndicatorComparativeFindingApplication,
        ):
            raise TypeError(
                "finding_application must be an "
                "IndicatorComparativeFindingApplication"
            )

        if not isinstance(
            hypothesis_evaluation_application,
            HypothesisEvaluationApplication,
        ):
            raise TypeError(
                "hypothesis_evaluation_application "
                "must be a "
                "HypothesisEvaluationApplication"
            )

        self._finding_application = (
            finding_application
        )
        self._hypothesis_evaluation_application = (
            hypothesis_evaluation_application
        )

    def run(
        self,
        *,
        hypothesis_id: str,
        requests: tuple[
            IndicatorComparativeFindingRequest,
            ...,
        ],
        correlation_id: str | None = None,
    ) -> HypothesisEvaluation:
        normalized_hypothesis_id = (
            self._normalize_hypothesis_id(
                hypothesis_id
            )
        )
        normalized_requests = (
            self._normalize_requests(requests)
        )
        findings = tuple(
            self._finding_application.run(
                hypothesis_id=normalized_hypothesis_id,
                market_specifications=(
                    request.market_specifications
                ),
                indicator_id=request.indicator_id,
                outcome_specification=(
                    request.outcome_specification
                ),
                horizon=request.horizon,
                statement=request.statement,
                applicable_markets=(
                    request.applicable_markets
                ),
                analysis_pipeline_version=(
                    request.analysis_pipeline_version
                ),
                correlation_id=correlation_id,
            )
            for request in normalized_requests
        )

        return (
            self._hypothesis_evaluation_application.run(
                findings=findings,
            )
        )

    @staticmethod
    def _normalize_hypothesis_id(
        value: object,
    ) -> str:
        if not isinstance(value, str):
            raise TypeError(
                "hypothesis_id must be a string"
            )

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                "hypothesis_id must not be empty"
            )

        return normalized

    @staticmethod
    def _normalize_requests(
        value: object,
    ) -> tuple[
        IndicatorComparativeFindingRequest,
        ...,
    ]:
        if not isinstance(value, tuple):
            raise TypeError(
                "requests must be a tuple"
            )

        if not value:
            raise ValueError(
                "requests must not be empty"
            )

        if any(
            not isinstance(
                request,
                IndicatorComparativeFindingRequest,
            )
            for request in value
        ):
            raise TypeError(
                "each request must be an "
                "IndicatorComparativeFindingRequest"
            )

        return value