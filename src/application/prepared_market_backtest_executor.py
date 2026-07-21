from __future__ import annotations

import pandas as pd

from src.backtest import (
    BacktestEngine,
    ExecutionPolicy,
    Statistics,
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

class PreparedMarketBacktestExecutor:
    """
    Executes one market experiment using an already loaded dataset.

    The executor does not load market data and therefore cannot create
    duplicate dataset retrievals inside one research session.
    """

    def __init__(
        self,
        *,
        specification: MarketExperimentSpecification,
        market_data: pd.DataFrame,
        signal_provider: MarketSignalProvider,
    ) -> None:
        if market_data.empty:
            raise ValueError(
                "market_data cannot be empty"
            )

        self.specification = specification
        self.market_data = market_data
        self.signal_provider = signal_provider

    def __call__(
        self,
        experiment: Experiment,
    ) -> ExperimentResult:
        signaled_data = self.signal_provider.generate(
            data=self.market_data,
            specification=self.specification,
        )

        execution_policy = ExecutionPolicy(
            stop_loss_percent=(
                self.specification.stop_loss_percent
            ),
            take_profit_percent=(
                self.specification.take_profit_percent
            ),
            max_holding_bars=(
                self.specification.max_holding_bars
            ),
        )

        trades = BacktestEngine().run(
            data=signaled_data,
            symbol=self.specification.symbol,
            timeframe=self.specification.timeframe,
            execution_policy=execution_policy,
        )

        metrics = Statistics(trades).calculate()

        success = bool(
            metrics["net_profit"] > 0
        )

        if success:
            conclusion = (
                "The experiment produced a positive "
                "net profit."
            )
        else:
            conclusion = (
                "The experiment did not produce a positive "
                "net profit."
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

        
           
