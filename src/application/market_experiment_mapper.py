from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
)
from src.research import Experiment, Hypothesis, Question


@dataclass(frozen=True)
class MappedMarketExperiment:
    """
    Research-core objects created from one market specification.
    """

    question: Question
    hypothesis: Hypothesis
    experiment: Experiment


@dataclass(frozen=True)
class MappedMarketCampaign:
    """
    Research-core objects created from multiple market specifications.
    """

    question: Question
    hypothesis: Hypothesis
    experiments: tuple[Experiment, ...]


class MarketExperimentMapper:
    """
    Maps application-level market specifications to research-core objects.

    Market-specific settings are stored in Experiment.parameters so the
    generic research core does not need to know about market execution
    details.
    """

    def map(
        self,
        specification: MarketExperimentSpecification,
    ) -> MappedMarketExperiment:
        question = self.map_question(
            specification,
        )

        hypothesis = self.map_hypothesis(
            specification,
            question=question,
        )

        experiment = self.map_experiment(
            specification,
            hypothesis=hypothesis,
        )

        return MappedMarketExperiment(
            question=question,
            hypothesis=hypothesis,
            experiment=experiment,
        )

    def map_campaign(
        self,
        specifications: Sequence[
            MarketExperimentSpecification
        ],
    ) -> MappedMarketCampaign:
        if not specifications:
            raise ValueError(
                "specifications must contain at least one "
                "market experiment specification"
            )

        self._validate_campaign_specifications(
            specifications,
        )

        first_specification = specifications[0]

        question = self.map_question(
            first_specification,
        )

        hypothesis = self.map_hypothesis(
            first_specification,
            question=question,
        )

        experiments = tuple(
            self.map_experiment(
                specification,
                hypothesis=hypothesis,
            )
            for specification in specifications
        )

        return MappedMarketCampaign(
            question=question,
            hypothesis=hypothesis,
            experiments=experiments,
        )

    def map_question(
        self,
        specification: MarketExperimentSpecification,
    ) -> Question:
        return Question(
            title=specification.question_title,
            description=specification.question_description,
            tags=list(specification.tags),
        )

    def map_hypothesis(
        self,
        specification: MarketExperimentSpecification,
        *,
        question: Question,
    ) -> Hypothesis:
        return Hypothesis(
            question_id=question.id,
            title=specification.hypothesis_title,
            description=specification.hypothesis_description,
            expected_result=specification.expected_result,
            tags=list(specification.tags),
        )

    def map_experiment(
        self,
        specification: MarketExperimentSpecification,
        *,
        hypothesis: Hypothesis,
    ) -> Experiment:
        return Experiment(
            hypothesis_id=hypothesis.id,
            title=specification.experiment_title,
            description=specification.experiment_description,
            parameters=self._build_experiment_parameters(
                specification,
            ),
            tags=list(specification.tags),
        )

    def _validate_campaign_specifications(
        self,
        specifications: Sequence[
            MarketExperimentSpecification
        ],
    ) -> None:
        first = specifications[0]

        for specification in specifications[1:]:
            if (
                specification.question_title
                != first.question_title
                or specification.question_description
                != first.question_description
            ):
                raise ValueError(
                    "All campaign specifications must describe "
                    "the same research question"
                )

            if (
                specification.hypothesis_title
                != first.hypothesis_title
                or specification.hypothesis_description
                != first.hypothesis_description
                or specification.expected_result
                != first.expected_result
            ):
                raise ValueError(
                    "All campaign specifications must describe "
                    "the same hypothesis"
                )

    def _build_experiment_parameters(
        self,
        specification: MarketExperimentSpecification,
    ) -> dict[str, Any]:
        return {
            "executor_type": specification.executor_type,
            "data_source": specification.data_source,
            "symbol": specification.symbol,
            "timeframe": specification.timeframe,
            "start_at": specification.start_at,
            "end_at": specification.end_at,
            "entry_rule": specification.entry_rule,
            "exit_rule": specification.exit_rule,
            "direction": specification.direction.value,
            "stop_loss_percent": specification.stop_loss_percent,
            "take_profit_percent": specification.take_profit_percent,
            "max_holding_bars": specification.max_holding_bars,
            "commission_percent": specification.commission_percent,
            "slippage_percent": specification.slippage_percent,
            "strategy_parameters": dict(
                specification.strategy_parameters,
            ),
        }
