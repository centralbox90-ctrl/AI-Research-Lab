from collections.abc import Callable

from src.backtest import (
    BacktestEngine,
    ExecutionPolicy,
    Statistics,
)
from src.application.market_data_provider import (
    MarketDataProvider,
)
from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
)
from src.application.market_signal_provider import (
    MarketSignalProvider,
)
from src.research import (
    Experiment,
    ExperimentResult,
)

class MarketBacktestExecutor:
    """
    Executes one market experiment through application boundaries.

    Flow:

    specification
        ↓
    market data provider
        ↓
    signal provider
        ↓
    execution policy
        ↓
    backtest engine
        ↓
    experiment result
    """

    def __init__(
        self,
        specification: MarketExperimentSpecification,
        data_provider: MarketDataProvider,
        signal_provider: MarketSignalProvider,
    ) -> None:

        self.specification = specification
        self.data_provider = data_provider
        self.signal_provider = signal_provider

    def __call__(
        self,
        experiment: Experiment,
    ) -> ExperimentResult:

        data = self.data_provider.load(
            self.specification,
        )

        prepared_data = self.signal_provider.generate(
            data=data,
            specification=self.specification,
        )

        policy = ExecutionPolicy(
            stop_loss_percent=(
                self.specification.stop_loss_percent
            ),
            take_profit_percent=(
                self.specification.take_profit_percent
            ),
            max_holding_bars=(
                self.specification.max_holding_bars
            ),
            commission_percent=(
                self.specification.commission_percent
            ),
            slippage_percent=(
                self.specification.slippage_percent
            ),
        )

        trades = BacktestEngine().run(
            data=prepared_data,
            symbol=self.specification.symbol,
            timeframe=self.specification.timeframe,
            execution_policy=policy,
        )

        metrics = Statistics(trades).calculate()

        success = bool(
            metrics["total_trades"] > 0
            and metrics["net_profit"] > 0
        )

        conclusion = (
            "Hypothesis supported"
            if success
            else "Hypothesis not supported"
        )

        return ExperimentResult(
            experiment_id=experiment.id,
            success=success,
            metrics=metrics,
            observations={
                "profit_percent": [
                    float(trade.profit_percent)
                    for trade in trades
                ],
                "exit_reasons": [
                    trade.exit_reason
                    for trade in trades
                ],
            },
            conclusion=conclusion,
        )
