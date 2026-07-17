from src.application.market_backtest_executor import (
    MarketBacktestExecutor,
)
from src.application.market_data_provider import (
    MarketDataProvider,
)
from src.application.market_experiment_executor import (
    MarketExperimentExecutorFactory,
)
from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
)
from src.application.market_signal_provider import (
    MarketSignalProvider,
)


class MarketBacktestExecutorFactory(
    MarketExperimentExecutorFactory,
):
    """
    Factory for creating market backtest executors.

    Responsible only for dependency construction.
    It does not execute experiments.
    """

    def __init__(
        self,
        data_provider: MarketDataProvider,
        signal_provider: MarketSignalProvider,
    ) -> None:
        self.data_provider = data_provider
        self.signal_provider = signal_provider

    def create(
        self,
        specification: MarketExperimentSpecification,
    ) -> MarketBacktestExecutor:
        return MarketBacktestExecutor(
            specification=specification,
            data_provider=self.data_provider,
            signal_provider=self.signal_provider,
        )