from __future__ import annotations

from src.application.indicator_comparative_hypothesis_evaluation_application import (
    IndicatorComparativeHypothesisEvaluationApplication,
)
from src.application.market_data_provider import (
    CanonicalMarketDatasetProvider,
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