from typing import Protocol

import pandas as pd

from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
)


class MarketSignalProvider(Protocol):
    """
    Produces backtest-ready market signals for one specification.

    Implementations receive raw market data and return a new DataFrame
    containing the AI_prediction column expected by BacktestEngine.

    The provider may use indicators, registered rules, machine-learning
    models, or another controlled signal-generation mechanism.

    It does not execute trades, evaluate hypotheses, persist research
    cycles, or mutate the supplied source DataFrame.
    """

    def generate(
        self,
        data: pd.DataFrame,
        specification: MarketExperimentSpecification,
    ) -> pd.DataFrame:
        """
        Return market data containing a valid AI_prediction column.
        """