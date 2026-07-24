from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
)
from src.research.research_planner import (
    CampaignExperimentSpecification,
    ResearchCampaignPlan,
)


class MarketExperimentSpecificationResolver(Protocol):
    """
    Resolves one planned experiment into a market specification.
    """

    def resolve(
        self,
        planned_specification: CampaignExperimentSpecification,
    ) -> MarketExperimentSpecification:
        ...


@dataclass(frozen=True, slots=True)
class ResolvedMarketExperiment:
    """
    Binds an executable market specification to its source plan item.
    """

    planned_specification: CampaignExperimentSpecification
    market_specification: MarketExperimentSpecification

    def __post_init__(self) -> None:
        if not isinstance(
            self.planned_specification,
            CampaignExperimentSpecification,
        ):
            raise TypeError(
                "planned_specification must be a "
                "CampaignExperimentSpecification"
            )

        if not isinstance(
            self.market_specification,
            MarketExperimentSpecification,
        ):
            raise TypeError(
                "market_specification must be a "
                "MarketExperimentSpecification"
            )

        if (
            self.market_specification.symbol
            != self.planned_specification.instrument
        ):
            raise ValueError(
                "resolved market specification symbol must match "
                "the planned instrument"
            )

        if (
            self.market_specification.timeframe
            != self.planned_specification.timeframe
        ):
            raise ValueError(
                "resolved market specification timeframe must match "
                "the planned timeframe"
            )


@dataclass(frozen=True, slots=True)
class ResolvedMarketCampaignPlan:
    """
    Application-level market resolution of a research campaign plan.
    """

    research_plan: ResearchCampaignPlan
    experiments: tuple[ResolvedMarketExperiment, ...]

    def __post_init__(self) -> None:
        if not isinstance(
            self.research_plan,
            ResearchCampaignPlan,
        ):
            raise TypeError(
                "research_plan must be a ResearchCampaignPlan"
            )

        if not isinstance(self.experiments, tuple):
            raise TypeError("experiments must be a tuple")

        if not self.experiments:
            raise ValueError("experiments must not be empty")

        if any(
            not isinstance(
                experiment,
                ResolvedMarketExperiment,
            )
            for experiment in self.experiments
        ):
            raise TypeError(
                "experiments must contain only "
                "ResolvedMarketExperiment values"
            )

        resolved_ids = tuple(
            experiment.planned_specification.id
            for experiment in self.experiments
        )

        if resolved_ids != self.research_plan.experiment_ids:
            raise ValueError(
                "resolved experiments must preserve the complete "
                "research plan order"
            )

    @property
    def market_specifications(
        self,
    ) -> tuple[MarketExperimentSpecification, ...]:
        return tuple(
            experiment.market_specification
            for experiment in self.experiments
        )


class ResearchCampaignPlanMarketAdapter:
    """
    Resolves a research campaign plan at the application boundary.
    """

    def __init__(
        self,
        resolver: MarketExperimentSpecificationResolver,
    ) -> None:
        if not callable(
            getattr(resolver, "resolve", None)
        ):
            raise TypeError(
                "resolver must provide a callable resolve method"
            )

        self._resolver = resolver

    def adapt(
        self,
        plan: ResearchCampaignPlan,
    ) -> ResolvedMarketCampaignPlan:
        if not isinstance(plan, ResearchCampaignPlan):
            raise TypeError(
                "plan must be a ResearchCampaignPlan"
            )

        experiments = tuple(
            ResolvedMarketExperiment(
                planned_specification=planned_specification,
                market_specification=self._resolver.resolve(
                    planned_specification
                ),
            )
            for planned_specification
            in plan.experiment_specifications
        )

        return ResolvedMarketCampaignPlan(
            research_plan=plan,
            experiments=experiments,
        )
