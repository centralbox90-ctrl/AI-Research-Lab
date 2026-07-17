from datetime import datetime, timezone

from src.application import (
    MarketExperimentExecutor,
    MarketExperimentExecutorFactory,
    MarketExperimentSpecification,
    MarketPositionDirection,
)
from src.research import Experiment, ExperimentResult


class ExecutorImplementation:
    def __call__(
        self,
        experiment: Experiment,
    ) -> ExperimentResult:
        return ExperimentResult(
            experiment_id=experiment.id,
            success=True,
            metrics={
                "total_trades": 10.0,
                "net_profit": 5.0,
            },
            observations={
                "profit_percent": [
                    0.5,
                    1.0,
                    -0.25,
                ],
            },
            conclusion="Hypothesis supported",
        )


class FactoryImplementation:
    def create(
        self,
        specification: MarketExperimentSpecification,
    ) -> MarketExperimentExecutor:
        return ExecutorImplementation()


def build_specification() -> MarketExperimentSpecification:
    return MarketExperimentSpecification(
        executor_type="market_backtest",
        question_title=(
            "Does the registered market condition predict a rebound?"
        ),
        question_description=(
            "Test whether the registered entry condition is followed "
            "by positive trade returns."
        ),
        hypothesis_title=(
            "The registered market condition precedes positive returns"
        ),
        hypothesis_description=(
            "The selected market condition is expected to produce "
            "positive historical trade results."
        ),
        expected_result=(
            "The experiment produces positive net profit with "
            "a non-zero number of trades."
        ),
        experiment_title="Historical market backtest",
        experiment_description=(
            "Run registered entry and exit rules on historical data."
        ),
        data_source="historical_csv",
        symbol="BTCUSDT",
        timeframe="1h",
        start_at=datetime(
            2024,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        end_at=datetime(
            2024,
            12,
            31,
            tzinfo=timezone.utc,
        ),
        entry_rule="registered_entry_rule",
        exit_rule="registered_exit_rule",
        direction=MarketPositionDirection.LONG,
        stop_loss_percent=1.0,
        take_profit_percent=2.0,
        max_holding_bars=24,
        commission_percent=0.1,
        slippage_percent=0.05,
        strategy_parameters={
            "period": 14,
        },
        tags=(
            "btc",
            "historical-backtest",
        ),
    )


def test_market_experiment_executor_defines_callable_contract() -> None:
    executor: MarketExperimentExecutor = ExecutorImplementation()

    experiment = Experiment(
        title="Historical market backtest",
    )

    result = executor(experiment)

    assert result.experiment_id == experiment.id
    assert result.success is True
    assert result.metrics["total_trades"] == 10.0
    assert result.metrics["net_profit"] == 5.0


def test_market_experiment_executor_factory_builds_executor() -> None:
    factory: MarketExperimentExecutorFactory = FactoryImplementation()

    specification = build_specification()
    executor = factory.create(specification)

    experiment = Experiment(
        title=specification.experiment_title,
    )

    result = executor(experiment)

    assert result.experiment_id == experiment.id
    assert result.success is True