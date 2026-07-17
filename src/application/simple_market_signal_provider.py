import pandas as pd

from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
)
from src.application.market_signal_provider import (
    MarketSignalProvider,
)


class SimpleMarketSignalProvider(
    MarketSignalProvider,
):
    """
    Generates simple rule-based development signals.

    This implementation exists only to validate the complete research
    execution pipeline.

    It does not represent a trading strategy.
    """

    def generate(
        self,
        data: pd.DataFrame,
        specification: MarketExperimentSpecification,
    ) -> pd.DataFrame:
        """
        Return data with AI_prediction column.
        """

        prepared = data.copy()

        previous_close = (
            prepared["Close"]
            .shift(1)
        )

        prepared["AI_prediction"] = 0

        prepared.loc[
            prepared["Close"] > previous_close,
            "AI_prediction",
        ] = 1

        prepared.loc[
            prepared["Close"] < previous_close,
            "AI_prediction",
        ] = -1

        prepared["AI_prediction"] = (
            prepared["AI_prediction"]
            .fillna(0)
            .astype(int)
        )

        return prepared