from __future__ import annotations

from src.application.experiment_execution_factory import (
    ExperimentExecutionFactory,
)
from src.application.experiment_execution_recorder import (
    ExperimentExecutionRecorder,
)
from src.application.indicator_comparative_execution_tracker import (
    IndicatorComparativeExecutionTracker,
)
from src.application.indicator_comparative_finding_application import (
    IndicatorComparativeFindingApplication,
)
from src.application.indicator_comparative_evidence_application import (
    IndicatorComparativeEvidenceApplication,
)
from src.application.indicator_comparative_evidence_service import (
    IndicatorComparativeEvidenceService,
)
from src.application.indicator_comparative_research_application import (
    IndicatorComparativeResearchApplication,
)
from src.application.indicator_comparative_research_service import (
    IndicatorComparativeResearchService,
)
from src.application.market_data_provider import (
    CanonicalMarketDatasetProvider,
)
from src.application.indicator_research_execution_factory import (
    IndicatorResearchExecutionFactory,
)
from src.application.system_clock import (
    SystemClock,
)
from src.indicators.catalog import (
    IndicatorCatalog,
)
from src.indicators.discovery import (
    discover_indicators,
)


from src.research.comparative_evaluation_plan import (
    ComparativeEvaluationPlan,
)
from src.research.comparative_evidence_evaluator import (
    ComparativeEvidenceEvaluator,
)
from src.research.comparative_statistical_evaluator import (
    ComparativeStatisticalEvaluator,
)
from src.research.finding_evaluator import (
    FindingEvaluator,
)

def build_default_indicator_comparative_finding_application(
    *,
    data_provider: CanonicalMarketDatasetProvider,
    evaluation_plan: ComparativeEvaluationPlan = (
        ComparativeEvaluationPlan()
    ),
    execution_recorder: (
        ExperimentExecutionRecorder | None
    ) = None,
    code_version: str = "development",
) -> IndicatorComparativeFindingApplication:
    """Build the replicated comparative Finding application."""

    return IndicatorComparativeFindingApplication(
        evidence_application=(
            build_default_indicator_comparative_evidence_application(
                data_provider=data_provider,
                evaluation_plan=evaluation_plan,
                execution_recorder=(
                    execution_recorder
                ),
                code_version=code_version,
            )
        ),
        finding_evaluator=FindingEvaluator(),
    )


def build_default_indicator_comparative_evidence_application(
    *,
    data_provider: CanonicalMarketDatasetProvider,
    evaluation_plan: ComparativeEvaluationPlan = (
        ComparativeEvaluationPlan()
    ),
    execution_recorder: (
        ExperimentExecutionRecorder | None
    ) = None,
    code_version: str = "development",
) -> IndicatorComparativeEvidenceApplication:
    """Build the replicated comparative Evidence application."""

    return IndicatorComparativeEvidenceApplication(
        research_application=(
            build_default_indicator_comparative_research_application(
                data_provider=data_provider,
                evaluation_plan=evaluation_plan,
                execution_recorder=(
                    execution_recorder
                ),
                code_version=code_version,
            )
        ),
        evidence_service=(
            build_default_indicator_comparative_evidence_service()
        ),
    )


def build_default_indicator_comparative_evidence_service(
) -> IndicatorComparativeEvidenceService:
    """Build the default comparative Evidence service."""

    return IndicatorComparativeEvidenceService(
        evidence_evaluator=(
            ComparativeEvidenceEvaluator()
        ),
    )


def build_default_indicator_comparative_research_service(
) -> IndicatorComparativeResearchService:
    """Build the default comparative research service."""

    indicator_catalog = _build_indicator_catalog()

    return _build_indicator_comparative_research_service(
        indicator_catalog
    )


def build_default_indicator_comparative_research_application(
    *,
    data_provider: CanonicalMarketDatasetProvider,
    evaluation_plan: ComparativeEvaluationPlan = (
        ComparativeEvaluationPlan()
    ),
    execution_recorder: (
        ExperimentExecutionRecorder | None
    ) = None,
    code_version: str = "development",
) -> IndicatorComparativeResearchApplication:
    """Build the default comparative research application."""

    indicator_catalog = _build_indicator_catalog()
    research_service = (
        _build_indicator_comparative_research_service(
            indicator_catalog
        )
    )
    execution_tracker = None

    if execution_recorder is not None:
        clock = SystemClock()
        execution_tracker = (
            IndicatorComparativeExecutionTracker(
                research_service=research_service,
                execution_factory=(
                    ExperimentExecutionFactory(
                        clock=clock,
                    )
                ),
                execution_recorder=(
                    execution_recorder
                ),
                clock=clock,
            )
        )

    return IndicatorComparativeResearchApplication(
        data_provider=data_provider,
        indicator_catalog=indicator_catalog,
        research_service=research_service,
        evaluation_plan=evaluation_plan,
        statistical_evaluator=(
            ComparativeStatisticalEvaluator()
        ),
        execution_tracker=execution_tracker,
        code_version=code_version,
    )


def _build_indicator_catalog() -> IndicatorCatalog:
    return IndicatorCatalog(
        discover_indicators(),
    )


def _build_indicator_comparative_research_service(
    indicator_catalog: IndicatorCatalog,
) -> IndicatorComparativeResearchService:
    research_execution_service = (
        IndicatorResearchExecutionFactory(
            indicator_catalog=indicator_catalog,
        ).create()
    )

    return IndicatorComparativeResearchService(
        research_execution_service=(
            research_execution_service
        ),
    )
