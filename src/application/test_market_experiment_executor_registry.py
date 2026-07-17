from datetime import datetime, timezone

import pytest

from src.application import (
    MarketExperimentExecutor,
    MarketExperimentExecutorFactory,
    MarketExperimentExecutorRegistry,
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
                "total_trades": 1.0,
                "net_profit": 1.0,
            },
            observations={
                "profit_percent": [1.0],
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
        question_title="Does the condition predict positive returns?",
        question_description=(
            "Test whether the registered condition produces "
            "positive historical trade returns."
        ),
        hypothesis_title="The condition predicts positive returns",
        hypothesis_description=(
            "The registered market condition is expected to produce "
            "positive results."
        ),
        expected_result=(
            "Positive net profit with a non-zero number of trades."
        ),
        experiment_title="Historical market backtest",
        experiment_description=(
            "Run registered rules against historical market data."
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
    )


def test_registry_registers_and_resolves_factory() -> None:
    registry = MarketExperimentExecutorRegistry()
    factory = FactoryImplementation()

    registry.register(
        executor_type="market_backtest",
        factory=factory,
    )

    resolved_factory = registry.get("market_backtest")

    assert resolved_factory is factory


def test_registry_factory_builds_executor_for_specification() -> None:
    registry = MarketExperimentExecutorRegistry()
    factory: MarketExperimentExecutorFactory = FactoryImplementation()

    registry.register(
        executor_type="market_backtest",
        factory=factory,
    )

    specification = build_specification()
    executor = registry.get(
        specification.executor_type,
    ).create(specification)

    experiment = Experiment(
        title=specification.experiment_title,
    )

    result = executor(experiment)

    assert result.experiment_id == experiment.id
    assert result.success is True


def test_registry_rejects_duplicate_executor_type() -> None:
    registry = MarketExperimentExecutorRegistry()
    factory = FactoryImplementation()

    registry.register(
        executor_type="market_backtest",
        factory=factory,
    )

    with pytest.raises(
        ValueError,
        match="executor_type already registered: market_backtest",
    ):
        registry.register(
            executor_type="market_backtest",
            factory=factory,
        )


def test_registry_rejects_empty_executor_type() -> None:
    registry = MarketExperimentExecutorRegistry()

    with pytest.raises(
        ValueError,
        match="executor_type must be a non-empty string",
    ):
        registry.register(
            executor_type="   ",
            factory=FactoryImplementation(),
        )


def test_registry_rejects_unsupported_executor_type() -> None:
    registry = MarketExperimentExecutorRegistry()

    with pytest.raises(
        LookupError,
        match="unsupported executor_type: indicator_study",
    ):
        registry.get("indicator_study")


def test_registry_lists_executor_types_in_deterministic_order() -> None:
    registry = MarketExperimentExecutorRegistry()

    registry.register(
        executor_type="parameter_stability",
        factory=FactoryImplementation(),
    )
    registry.register(
        executor_type="market_backtest",
        factory=FactoryImplementation(),
    )

    assert registry.list_executor_types() == [
        "market_backtest",
        "parameter_stability",
    ]