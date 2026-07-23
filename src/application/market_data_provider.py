from typing import Protocol

import pandas as pd

from src.application.canonical_market_dataset import (
    CanonicalMarketDataset,
)

from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
)


class MarketDataProvider(Protocol):
    """
    Provides market data for one validated market experiment.

    Implementations may read historical files, databases, or external
    market-data APIs.

    The provider does not generate research signals, execute trades,
    evaluate hypotheses, or run research cycles.
    """

    def load(
        self,
        specification: MarketExperimentSpecification,
    ) -> pd.DataFrame:
        """
        Load market data for the supplied specification.
        """

class CanonicalMarketDatasetProvider(Protocol):
    """
    Provides one canonical market dataset for a research session.
    """

    def load(
        self,
        specification: MarketExperimentSpecification,
    ) -> CanonicalMarketDataset:
        """
        Load the canonical dataset for the supplied specification.
        """