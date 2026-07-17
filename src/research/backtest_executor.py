from collections.abc import Callable

import pandas as pd

from src.backtest.engine import BacktestEngine
from src.backtest.statistics import Statistics
from src.research.experiment import Experiment
from src.research.experiment_result import ExperimentResult


class BacktestExperimentExecutor:
    """
    Выполняет исследовательский эксперимент через BacktestEngine.

    Агрегированные показатели сохраняются в metrics.
    Результаты отдельных сделок сохраняются в observations
    для последующей статистической оценки.
    """

    def __init__(
        self,
        data_provider: Callable[[Experiment], pd.DataFrame],
        symbol: str,
        timeframe: str,
    ) -> None:
        self.data_provider = data_provider
        self.symbol = symbol
        self.timeframe = timeframe

    def __call__(self, experiment: Experiment) -> ExperimentResult:
        data = self.data_provider(experiment)

        trades = BacktestEngine().run(
            data=data,
            symbol=self.symbol,
            timeframe=self.timeframe,
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

        profit_percent_observations = [
            float(trade.profit_percent)
            for trade in trades
        ]

        return ExperimentResult(
            experiment_id=experiment.id,
            success=success,
            metrics=metrics,
            observations={
                "profit_percent": profit_percent_observations,
            },
            conclusion=conclusion,
        )