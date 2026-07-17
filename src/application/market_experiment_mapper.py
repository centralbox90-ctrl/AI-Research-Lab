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


class MarketExperimentMapper:
    """
    Maps an application-level market specification to research-core objects.

    Market-specific settings are stored in Experiment.parameters so the
    generic research core does not need to know about market execution
    details.
    """

    def map(
        self,
        specification: MarketExperimentSpecification,
    ) -> MappedMarketExperiment:
        question = Question(
            title=specification.question_title,
            description=specification.question_description,
            tags=list(specification.tags),
        )

        hypothesis = Hypothesis(
            question_id=question.id,
            title=specification.hypothesis_title,
            description=specification.hypothesis_description,
            expected_result=specification.expected_result,
            tags=list(specification.tags),
        )

        experiment = Experiment(
            hypothesis_id=hypothesis.id,
            title=specification.experiment_title,
            description=specification.experiment_description,
            parameters=self._build_experiment_parameters(
                specification,
            ),
            tags=list(specification.tags),
        )

        return MappedMarketExperiment(
            question=question,
            hypothesis=hypothesis,
            experiment=experiment,
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