from __future__ import annotations

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
        Return canonical market data with an AI_prediction column.

        The supplied DataFrame is not modified.
        """
        if "close" not in data.columns:
            raise ValueError(
                "canonical market data must contain "
                "the close column"
            )

        prepared = data.copy(deep=True)

        previous_close = (
            prepared["close"]
            .shift(1)
        )

        prepared["AI_prediction"] = 0

        prepared.loc[
            prepared["close"] > previous_close,
            "AI_prediction",
        ] = 1

        prepared.loc[
            prepared["close"] < previous_close,
            "AI_prediction",
        ] = -1

        prepared["AI_prediction"] = (
            prepared["AI_prediction"]
            .fillna(0)
            .astype(int)
        )

        return prepared