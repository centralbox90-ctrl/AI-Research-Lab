import pandas as pd

from src.application.market_data_provider import (
    MarketDataProvider,
)
from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
)
from src.data.loader import generate_market_data


class GeneratedMarketDataProvider(
    MarketDataProvider,
):
    """
    Provides deterministic development market data.

    This adapter wraps the existing market-data generator and exposes it
    through the MarketDataProvider application boundary.

    It does not create signals, execute trades, or run experiments.
    """

    def load(
        self,
        specification: MarketExperimentSpecification,
    ) -> pd.DataFrame:
        """
        Load generated market data for one experiment.
        """

        return generate_market_data(
            symbol=specification.symbol,
            timeframe=specification.timeframe,
        )