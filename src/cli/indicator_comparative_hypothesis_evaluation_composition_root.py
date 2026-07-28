from __future__ import annotations

from src.application.indicator_comparative_hypothesis_evaluation_application import (
    IndicatorComparativeHypothesisEvaluationApplication,
)
from src.application.market_data_provider import (
    CanonicalMarketDatasetProvider,
)
from src.application.promote_hypothesis_evaluation_to_knowledge import (
    PromoteHypothesisEvaluationToKnowledge,
)
from src.cli.run_indicator_comparative_hypothesis_evaluation_command import (
    RunIndicatorComparativeHypothesisEvaluationCommand,
)
from src.cli.hypothesis_evaluation_composition_root import (
    build_default_hypothesis_evaluation_application,
)
from src.cli.indicator_comparative_research_composition_root import (
    build_default_indicator_comparative_finding_application,
)
from src.research.comparative_evaluation_plan import (
    ComparativeEvaluationPlan,
)
from src.research.hypothesis_evaluation_plan import (
    HypothesisEvaluationPlan,
)


def build_default_indicator_comparative_hypothesis_evaluation_command(
    *,
    data_provider: CanonicalMarketDatasetProvider,
    promotion_application: (
        PromoteHypothesisEvaluationToKnowledge
        | None
    ) = None,
    comparative_evaluation_plan: ComparativeEvaluationPlan = (
        ComparativeEvaluationPlan()
    ),
    hypothesis_evaluation_plan: HypothesisEvaluationPlan = (
        HypothesisEvaluationPlan()
    ),
) -> RunIndicatorComparativeHypothesisEvaluationCommand:
    """Build the complete comparative evaluation CLI command."""

    return RunIndicatorComparativeHypothesisEvaluationCommand(
        application=(
            build_default_indicator_comparative_hypothesis_evaluation_application(
                data_provider=data_provider,
                comparative_evaluation_plan=(
                    comparative_evaluation_plan
                ),
                hypothesis_evaluation_plan=(
                    hypothesis_evaluation_plan
                ),
            )
        ),
        promotion_application=(
            promotion_application
        ),
    )


def build_default_indicator_comparative_hypothesis_evaluation_application(
    *,
    data_provider: CanonicalMarketDatasetProvider,
    comparative_evaluation_plan: ComparativeEvaluationPlan = (
        ComparativeEvaluationPlan()
    ),
    hypothesis_evaluation_plan: HypothesisEvaluationPlan = (
        HypothesisEvaluationPlan()
    ),
) -> IndicatorComparativeHypothesisEvaluationApplication:
    """
    Build the complete comparative hypothesis evaluation application.
    """

    return IndicatorComparativeHypothesisEvaluationApplication(
        finding_application=(
            build_default_indicator_comparative_finding_application(
                data_provider=data_provider,
                evaluation_plan=comparative_evaluation_plan,
            )
        ),
        hypothesis_evaluation_application=(
            build_default_hypothesis_evaluation_application(
                plan=hypothesis_evaluation_plan,
            )
        ),
    )
