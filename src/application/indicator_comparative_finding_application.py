from __future__ import annotations

from src.application.indicator_comparative_evidence_application import (
    IndicatorComparativeEvidenceApplication,
)
from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
)
from src.research.finding import Finding
from src.research.finding_evaluator import (
    FindingEvaluator,
)
from src.research.outcome_specification import (
    ForwardReturnSpecification,
)


class IndicatorComparativeFindingApplication:
    """
    Runs replicated comparative research through a Finding.
    """

    def __init__(
        self,
        *,
        evidence_application: (
            IndicatorComparativeEvidenceApplication
        ),
        finding_evaluator: FindingEvaluator,
    ) -> None:
        if not isinstance(
            evidence_application,
            IndicatorComparativeEvidenceApplication,
        ):
            raise TypeError(
                "evidence_application must be an "
                "IndicatorComparativeEvidenceApplication"
            )

        if not isinstance(
            finding_evaluator,
            FindingEvaluator,
        ):
            raise TypeError(
                "finding_evaluator must be a "
                "FindingEvaluator"
            )

        self._evidence_application = (
            evidence_application
        )
        self._finding_evaluator = finding_evaluator

    def run(
        self,
        *,
        hypothesis_id: str,
        market_specifications: tuple[
            MarketExperimentSpecification,
            ...,
        ],
        indicator_id: str,
        outcome_specification: (
            ForwardReturnSpecification
        ),
        horizon: int,
        statement: str,
        applicable_markets: tuple[str, ...],
        correlation_id: str | None = None,
        analysis_pipeline_version: str = (
            FindingEvaluator
            .DEFAULT_PIPELINE_VERSION
        ),
    ) -> Finding:
        evidence = self._evidence_application.run(
            hypothesis_id=hypothesis_id,
            market_specifications=(
                market_specifications
            ),
            indicator_id=indicator_id,
            outcome_specification=(
                outcome_specification
            ),
            horizon=horizon,
            correlation_id=correlation_id,
        )

        return self._finding_evaluator.evaluate(
            evidence=evidence,
            statement=statement,
            applicable_markets=applicable_markets,
            analysis_pipeline_version=(
                analysis_pipeline_version
            ),
        )