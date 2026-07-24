from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
)
from src.application.research_campaign_plan_market_adapter import (
    ResearchCampaignPlanMarketAdapter,
    ResolvedMarketCampaignPlan,
    ResolvedMarketExperiment,
)
from src.research.campaign_design import CampaignDesign
from src.research.research_planner import (
    ResearchCampaignPlan,
    ResearchPlanner,
)


class MarketResearchExperimentRunner(Protocol):
    """
    Executes one fully resolved market experiment specification.
    """

    def execute(
        self,
        specification: MarketExperimentSpecification,
    ) -> object:
        ...


@dataclass(frozen=True, slots=True)
class MarketResearchCampaignExperimentResult:
    """
    One execution result linked to its resolved planned experiment.
    """

    resolved_experiment: ResolvedMarketExperiment
    result: object

    def __post_init__(self) -> None:
        if not isinstance(
            self.resolved_experiment,
            ResolvedMarketExperiment,
        ):
            raise TypeError(
                "resolved_experiment must be a "
                "ResolvedMarketExperiment"
            )


@dataclass(frozen=True, slots=True)
class MarketResearchCampaignResult:
    """
    Result of executing every experiment in one resolved campaign.
    """

    resolved_plan: ResolvedMarketCampaignPlan
    experiment_results: tuple[
        MarketResearchCampaignExperimentResult,
        ...,
    ]

    def __post_init__(self) -> None:
        if not isinstance(
            self.resolved_plan,
            ResolvedMarketCampaignPlan,
        ):
            raise TypeError(
                "resolved_plan must be a "
                "ResolvedMarketCampaignPlan"
            )

        if not isinstance(
            self.experiment_results,
            tuple,
        ):
            raise TypeError(
                "experiment_results must be a tuple"
            )

        if not self.experiment_results:
            raise ValueError(
                "experiment_results must not be empty"
            )

        if any(
            not isinstance(
                experiment_result,
                MarketResearchCampaignExperimentResult,
            )
            for experiment_result
            in self.experiment_results
        ):
            raise TypeError(
                "experiment_results must contain only "
                "MarketResearchCampaignExperimentResult values"
            )

        result_ids = tuple(
            experiment_result
            .resolved_experiment
            .planned_specification
            .id
            for experiment_result
            in self.experiment_results
        )

        if (
            result_ids
            != self.resolved_plan.research_plan.experiment_ids
        ):
            raise ValueError(
                "experiment results must preserve the complete "
                "resolved campaign plan order"
            )

    @property
    def research_plan(self) -> ResearchCampaignPlan:
        return self.resolved_plan.research_plan

    @property
    def results(self) -> tuple[object, ...]:
        return tuple(
            experiment_result.result
            for experiment_result
            in self.experiment_results
        )


class RunMarketResearchCampaign:
    """
    Plans, resolves, and executes one market research campaign.

    Resolution of the complete plan finishes before the first
    experiment is executed. Missing registrations therefore cannot
    produce a partially executed campaign.
    """

    def __init__(
        self,
        *,
        planner: ResearchPlanner,
        adapter: ResearchCampaignPlanMarketAdapter,
        runner: MarketResearchExperimentRunner,
    ) -> None:
        if not isinstance(planner, ResearchPlanner):
            raise TypeError(
                "planner must be a ResearchPlanner"
            )

        if not isinstance(
            adapter,
            ResearchCampaignPlanMarketAdapter,
        ):
            raise TypeError(
                "adapter must be a "
                "ResearchCampaignPlanMarketAdapter"
            )

        if not callable(
            getattr(runner, "execute", None)
        ):
            raise TypeError(
                "runner must provide a callable execute method"
            )

        self._planner = planner
        self._adapter = adapter
        self._runner = runner

    def execute(
        self,
        design: CampaignDesign,
    ) -> MarketResearchCampaignResult:
        if not isinstance(design, CampaignDesign):
            raise TypeError(
                "design must be a CampaignDesign"
            )

        plan = self._planner.plan(design)
        resolved_plan = self._adapter.adapt(plan)

        experiment_results = tuple(
            MarketResearchCampaignExperimentResult(
                resolved_experiment=resolved_experiment,
                result=self._runner.execute(
                    resolved_experiment.market_specification
                ),
            )
            for resolved_experiment
            in resolved_plan.experiments
        )

        return MarketResearchCampaignResult(
            resolved_plan=resolved_plan,
            experiment_results=experiment_results,
        )
