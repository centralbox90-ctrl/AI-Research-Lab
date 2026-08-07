from __future__ import annotations

from dataclasses import dataclass, replace

from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
)
from src.application.market_research_campaign_session import (
    MarketResearchCampaignSession,
)
from src.application.market_research_campaign_session_factory import (
    MarketResearchCampaignSessionFactory,
)
from src.indicators.catalog import IndicatorCatalog
from src.research.cycle_results import ResearchCycleResult
from src.research.engine import ResearchEngine
from src.research.experiment_comparator import (
    ExperimentComparator,
    RankedExperiment,
)
from src.research.specification_grid import (
    ResearchSpecificationGridFactory,
)
from src.research.specification import ResearchSpecification


@dataclass(frozen=True, slots=True)
class IndicatorParameterSearchResult:
    """Completed parameter search with a deterministic ranking."""

    indicator_id: str
    metric: str
    session: MarketResearchCampaignSession
    market_specifications: tuple[
        MarketExperimentSpecification,
        ...,
    ]
    cycles: tuple[ResearchCycleResult, ...]
    ranking: tuple[RankedExperiment, ...]

    @property
    def best(self) -> RankedExperiment:
        return self.ranking[0]

    @property
    def best_market_specification(
        self,
    ) -> MarketExperimentSpecification:
        for experiment, specification in zip(
            self.session.experiments,
            self.market_specifications,
            strict=True,
        ):
            if experiment.id == self.best.experiment.id:
                return specification

        raise RuntimeError(
            "best experiment has no market specification"
        )


class IndicatorParameterSearchApplication:
    """Run every combination declared by one indicator plugin."""

    def __init__(
        self,
        *,
        indicator_catalog: IndicatorCatalog,
        session_factory: MarketResearchCampaignSessionFactory,
        specification_grid_factory: (
            ResearchSpecificationGridFactory | None
        ) = None,
        research_engine: ResearchEngine | None = None,
        comparator: ExperimentComparator | None = None,
    ) -> None:
        self._indicator_catalog = indicator_catalog
        self._session_factory = session_factory
        self._specification_grid_factory = (
            specification_grid_factory
            or ResearchSpecificationGridFactory()
        )
        self._research_engine = research_engine or ResearchEngine()
        self._comparator = comparator or ExperimentComparator()

    def run(
        self,
        *,
        market_specification: MarketExperimentSpecification,
        indicator_id: str,
        metric: str = "net_profit",
        reverse: bool = True,
    ) -> IndicatorParameterSearchResult:
        if not isinstance(
            market_specification,
            MarketExperimentSpecification,
        ):
            raise TypeError(
                "market_specification must be a "
                "MarketExperimentSpecification"
            )

        normalized_indicator_id = self._normalize_text(
            indicator_id,
            field_name="indicator_id",
        )
        normalized_metric = self._normalize_text(
            metric,
            field_name="metric",
        )

        descriptor = self._indicator_catalog.get(
            normalized_indicator_id
        )
        research_specifications = (
            self._specification_grid_factory.create(
                descriptor
            )
        )
        market_specifications = tuple(
            self._bind_research_specification(
                market_specification=market_specification,
                research_specification=research_specification,
                position=position,
                total=len(research_specifications),
            )
            for position, research_specification in enumerate(
                research_specifications,
                start=1,
            )
        )

        session = self._session_factory.create(
            market_specifications
        )
        cycles = tuple(
            self._research_engine.run_campaign(
                question=session.question,
                hypothesis=session.hypothesis,
                campaign=session.campaign,
                experiments=list(session.experiments),
                executor=session.executor,
            )
        )
        ranking = tuple(
            self._comparator.rank(
                experiments=list(session.experiments),
                results=[cycle.result for cycle in cycles],
                metric=normalized_metric,
                reverse=reverse,
            )
        )

        return IndicatorParameterSearchResult(
            indicator_id=descriptor.id,
            metric=normalized_metric,
            session=session,
            market_specifications=market_specifications,
            cycles=cycles,
            ranking=ranking,
        )

    @staticmethod
    def _bind_research_specification(
        *,
        market_specification: MarketExperimentSpecification,
        research_specification: ResearchSpecification,
        position: int,
        total: int,
    ) -> MarketExperimentSpecification:
        fingerprint = research_specification.fingerprint
        return replace(
            market_specification,
            experiment_title=(
                f"{market_specification.experiment_title} "
                f"[{position}/{total}]"
            ),
            research_specification=research_specification,
            strategy_parameters={
                **market_specification.strategy_parameters,
                "research_specification_fingerprint": fingerprint,
            },
        )

    @staticmethod
    def _normalize_text(
        value: object,
        *,
        field_name: str,
    ) -> str:
        if not isinstance(value, str):
            raise TypeError(f"{field_name} must be a string")

        normalized = value.strip()
        if not normalized:
            raise ValueError(f"{field_name} must not be empty")

        return normalized
