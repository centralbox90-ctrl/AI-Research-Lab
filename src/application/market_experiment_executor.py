from typing import Protocol

from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
)
from src.research import Experiment, ExperimentResult


class MarketExperimentExecutor(Protocol):
    """
    Executes one research-core Experiment in a market environment.

    Implementations may use historical data, a backtest engine, or
    another controlled market-experiment infrastructure.

    The executor does not run the complete research cycle. It only
    produces an ExperimentResult for the supplied Experiment.
    """

    def __call__(
        self,
        experiment: Experiment,
    ) -> ExperimentResult:
        """
        Execute the experiment and return its result.
        """


class MarketExperimentExecutorFactory(Protocol):
    """
    Creates a market experiment executor from a validated specification.

    Implementations translate application-level market settings into
    concrete infrastructure dependencies without exposing those details
    to the research core or CLI.
    """

    def create(
        self,
        specification: MarketExperimentSpecification,
    ) -> MarketExperimentExecutor:
        """
        Build an executor for the supplied market specification.
        """