from __future__ import annotations

import json
from hashlib import sha256

from src.application.indicator_comparative_execution_specification import (
    IndicatorComparativeExecutionSpecification,
)
from src.application.indicator_comparative_execution_tracker import (
    IndicatorComparativeExecutionTracker,
)
from src.application.indicator_comparative_research_design import (
    IndicatorComparativeResearchDesign,
)
from src.application.indicator_comparative_research_result import (
    IndicatorComparativeResearchResult,
)
from src.application.indicator_comparative_research_service import (
    IndicatorComparativeResearchService,
)
from src.application.market_data_provider import (
    CanonicalMarketDatasetProvider,
)
from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
)
from src.indicators.catalog import IndicatorCatalog
from src.research.comparative_evaluation_plan import (
    ComparativeEvaluationPlan,
)
from src.research.comparative_statistical_evaluator import (
    ComparativeStatisticalEvaluator,
)
from src.research.outcome_specification import (
    ForwardReturnSpecification,
)
from src.research.specification_factory import (
    create_default_research_specification,
)


class IndicatorComparativeResearchApplication:
    """Coordinates one default comparative indicator research run."""

    def __init__(
        self,
        *,
        data_provider: CanonicalMarketDatasetProvider,
        indicator_catalog: IndicatorCatalog,
        research_service: IndicatorComparativeResearchService,
        statistical_evaluator: ComparativeStatisticalEvaluator,
        evaluation_plan: ComparativeEvaluationPlan = (
            ComparativeEvaluationPlan()
        ),
        execution_tracker: (
            IndicatorComparativeExecutionTracker
            | None
        ) = None,
        code_version: str = "development",
        executor_version: str = (
            "indicator-comparative-research:v1"
        ),
    ) -> None:
        if (
            execution_tracker is not None
            and not callable(
                getattr(
                    execution_tracker,
                    "execute",
                    None,
                )
            )
        ):
            raise TypeError(
                "execution_tracker must provide "
                "a callable execute method"
            )

        self._data_provider = data_provider
        self._indicator_catalog = indicator_catalog
        self._research_service = research_service
        self._statistical_evaluator = statistical_evaluator
        self._evaluation_plan = evaluation_plan
        self._execution_tracker = execution_tracker
        self._code_version = self._normalize_text(
            code_version,
            field_name="code_version",
        )
        self._executor_version = self._normalize_text(
            executor_version,
            field_name="executor_version",
        )

    def run(
        self,
        *,
        market_specification: MarketExperimentSpecification,
        indicator_id: str,
        outcome_specification: ForwardReturnSpecification,
        correlation_id: str | None = None,
    ) -> IndicatorComparativeResearchResult:
        if not isinstance(
            market_specification,
            MarketExperimentSpecification,
        ):
            raise TypeError(
                "market_specification must be a "
                "MarketExperimentSpecification"
            )

        if not isinstance(indicator_id, str):
            raise TypeError(
                "indicator_id must be a string"
            )

        normalized_indicator_id = indicator_id.strip()

        if not normalized_indicator_id:
            raise ValueError(
                "indicator_id must not be empty"
            )

        if not isinstance(
            outcome_specification,
            ForwardReturnSpecification,
        ):
            raise TypeError(
                "outcome_specification must be a "
                "ForwardReturnSpecification"
            )

        descriptor = self._indicator_catalog.get(
            normalized_indicator_id
        )
        research_specification = (
            create_default_research_specification(
                descriptor
            )
        )
        design = IndicatorComparativeResearchDesign(
            research_specification=(
                research_specification
            ),
            outcome_specification=(
                outcome_specification
            ),
        )
        dataset = self._data_provider.load(
            market_specification
        )

        if self._execution_tracker is None:
            analysis = self._research_service.run(
                dataset=dataset,
                design=design,
                symbol=market_specification.symbol,
                timeframe=market_specification.timeframe,
            )
        else:
            execution_specification = (
                IndicatorComparativeExecutionSpecification(
                    market_specification=(
                        market_specification
                    ),
                    research_specification=(
                        research_specification
                    ),
                    outcome_specification=(
                        outcome_specification
                    ),
                    baseline=design.baseline,
                )
            )
            analysis = (
                self._execution_tracker.execute(
                    dataset=dataset,
                    specification=(
                        execution_specification
                    ),
                    environment_fingerprint=(
                        self
                        ._build_execution_environment_fingerprint(
                            dataset
                        )
                    ),
                    correlation_id=correlation_id,
                )
            )
        statistical_evaluations = (
            self._statistical_evaluator.evaluate(
                analysis=analysis,
                research_fingerprint=(
                    research_specification.fingerprint
                ),
                plan=self._evaluation_plan,
                dataset_id=(
                    dataset.fingerprint
                    .dataset_fingerprint
                ),
            )
        )

        return IndicatorComparativeResearchResult(
            indicator_id=descriptor.id,
            symbol=market_specification.symbol,
            timeframe=market_specification.timeframe,
            research_specification=(
                research_specification
            ),
            dataset_fingerprint=(
                dataset.fingerprint
            ),
            data_quality_report=(
                dataset.quality_report
            ),
            analysis=analysis,
            evaluation_plan=self._evaluation_plan,
            statistical_evaluations=(
                statistical_evaluations
            ),
        )

    def _build_execution_environment_fingerprint(
        self,
        dataset: object,
    ) -> str:
        payload = {
            "schema_version": 1,
            "dataset_fingerprint": (
                dataset
                .fingerprint
                .dataset_fingerprint
            ),
            "code_version": self._code_version,
            "executor_version": (
                self._executor_version
            ),
        }
        serialized = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )

        return sha256(
            serialized.encode("utf-8")
        ).hexdigest()

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
