import pandas as pd

from src.application.indicator_comparative_evidence_application import (
    IndicatorComparativeEvidenceApplication,
)
from src.application.indicator_comparative_evidence_service import (
    IndicatorComparativeEvidenceService,
)
from src.application.indicator_comparative_research_application import (
    IndicatorComparativeResearchApplication,
)
from src.application.canonical_market_dataset import (
    CanonicalMarketDataset,
)
from src.application.market_dataset_quality import (
    MarketDatasetQualityAnalyzer,
)
from src.application.indicator_comparative_research_design import (
    IndicatorComparativeResearchDesign,
)
from src.application.indicator_comparative_research_service import (
    IndicatorComparativeResearchService,
)
from src.cli.indicator_comparative_research_composition_root import (
    build_default_indicator_comparative_evidence_application,
    build_default_indicator_comparative_evidence_service,
    build_default_indicator_comparative_research_application,
    build_default_indicator_comparative_research_service,
)
from src.indicators.implementations.rsi import INDICATOR
from src.research.comparative_evaluation_plan import (
    ComparativeEvaluationPlan,
)
from src.research.comparative_evidence_evaluator import (
    ComparativeEvidenceEvaluator,
)
from src.research.market_dataset_fingerprint import (
    DatasetFingerprintContext,
    MarketDatasetCanonicalizer,
    MarketDatasetFingerprinter,
)
from src.research.outcome_specification import (
    ForwardReturnSpecification,
)
from src.research.specification_factory import (
    create_default_research_specification,
)


def build_dataset(
    close: list[float],
) -> CanonicalMarketDataset:
    canonical = (
        MarketDatasetCanonicalizer()
        .canonicalize(
            pd.DataFrame(
                {
                    "timestamp": pd.date_range(
                        "2026-01-01",
                        periods=len(close),
                        freq="h",
                        tz="UTC",
                    ),
                    "open": close,
                    "high": close,
                    "low": close,
                    "close": close,
                    "tick_volume": [
                        100 + index
                        for index in range(len(close))
                    ],
                }
            )
        )
    )
    fingerprint = MarketDatasetFingerprinter().attach(
        canonical,
        DatasetFingerprintContext(
            symbol="EURUSD",
            timeframe="H1",
        ),
    )

    return CanonicalMarketDataset(
        data=canonical,
        fingerprint=fingerprint,
        quality_report=(
            MarketDatasetQualityAnalyzer().analyze(
                canonical
            )
        ),
    )


class StubDatasetProvider:
    def load(self, specification: object) -> object:
        raise AssertionError(
            "load must not run during composition"
        )


def test_builds_default_comparative_evidence_application(
) -> None:
    evaluation_plan = ComparativeEvaluationPlan(
        random_seed=11,
    )

    application = (
        build_default_indicator_comparative_evidence_application(
            data_provider=StubDatasetProvider(),
            evaluation_plan=evaluation_plan,
        )
    )

    assert isinstance(
        application,
        IndicatorComparativeEvidenceApplication,
    )
    assert isinstance(
        application._research_application,
        IndicatorComparativeResearchApplication,
    )
    assert (
        application
        ._research_application
        ._evaluation_plan
        is evaluation_plan
    )
    assert isinstance(
        application._evidence_service,
        IndicatorComparativeEvidenceService,
    )



def test_builds_default_comparative_research_application(
) -> None:
    evaluation_plan = ComparativeEvaluationPlan(
        random_seed=7,
    )

    application = (
        build_default_indicator_comparative_research_application(
            data_provider=StubDatasetProvider(),
            evaluation_plan=evaluation_plan,
        )
    )

    assert isinstance(
        application,
        IndicatorComparativeResearchApplication,
    )


    assert application._evaluation_plan is (
        evaluation_plan
    )


def test_builds_default_comparative_evidence_service(
) -> None:
    service = (
        build_default_indicator_comparative_evidence_service()
    )

    assert isinstance(
        service,
        IndicatorComparativeEvidenceService,
    )
    assert isinstance(
        service._evidence_evaluator,
        ComparativeEvidenceEvaluator,
    )


def test_builds_default_comparative_research_service(
) -> None:
    service = (
        build_default_indicator_comparative_research_service()
    )

    assert isinstance(
        service,
        IndicatorComparativeResearchService,
    )


def test_runs_default_rsi_comparative_pipeline(
) -> None:
    service = (
        build_default_indicator_comparative_research_service()
    )
    specification = (
        create_default_research_specification(
            INDICATOR
        )
    )
    design = IndicatorComparativeResearchDesign(
        research_specification=specification,
        outcome_specification=(
            ForwardReturnSpecification(
                horizons=(1, 3),
            )
        ),
    )

    close = (
        [
            100.0 + index
            for index in range(20)
        ]
        + [
            120.0 - (2.0 * index)
            for index in range(20)
        ]
    )
    dataset = build_dataset(close)

    analysis = service.run(
        dataset=dataset,
        design=design,
        symbol="EURUSD",
        timeframe="H1",
    )

    assert (
        analysis.candidate_result
        .observation_count
        >= 1
    )
    assert (
        analysis.baseline_result
        .observation_count
        == len(dataset.data) - 3
    )
    assert tuple(
        comparison.horizon
        for comparison in analysis.comparisons
    ) == (1, 3)
