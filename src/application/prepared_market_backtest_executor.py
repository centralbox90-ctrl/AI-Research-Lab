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
        execution_data = self._build_execution_data()

        prepared_data = self.signal_provider.generate(
            data=execution_data,
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

    def _build_execution_data(self) -> pd.DataFrame:
        """
        Build the temporary legacy execution view required by the
        current BacktestEngine.

        ResearchContext retains the canonical dataset. This mapping
        exists only at the legacy backtest boundary.
        """

        canonical_columns = {
            "timestamp",
            "open",
            "high",
            "low",
            "close",
            "tick_volume",
        }

        if canonical_columns.issubset(
            self.market_data.columns
        ):
            timestamps = pd.to_datetime(
                self.market_data["timestamp"],
                unit="ns",
                utc=True,
            )

            execution_data = pd.DataFrame(
                {
                    "Open": self.market_data[
                        "open"
                    ].to_numpy(copy=True),
                    "High": self.market_data[
                        "high"
                    ].to_numpy(copy=True),
                    "Low": self.market_data[
                        "low"
                    ].to_numpy(copy=True),
                    "Close": self.market_data[
                        "close"
                    ].to_numpy(copy=True),
                    "Volume": self.market_data[
                        "tick_volume"
                    ].to_numpy(copy=True),
                },
                index=pd.DatetimeIndex(timestamps),
            )

            execution_data.attrs.update(
                self.market_data.attrs
            )

            return execution_data

        return self.market_data