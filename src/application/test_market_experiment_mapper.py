from datetime import datetime, timezone

from src.application import (
    MarketExperimentMapper,
    MarketExperimentSpecification,
    MarketPositionDirection,
)


def build_specification() -> MarketExperimentSpecification:
    return MarketExperimentSpecification(
        executor_type="market_backtest",
        question_title="Does Williams oversold predict a rebound?",
        question_description=(
            "Test whether a Williams oversold condition is followed "
            "by positive trade returns."
        ),
        hypothesis_title=(
            "Williams oversold values precede positive returns"
        ),
        hypothesis_description=(
            "BTCUSDT should produce positive historical results after "
            "the registered oversold condition."
        ),
        expected_result=(
            "Positive net profit with a non-zero number of trades."
        ),
        experiment_title="Williams BTCUSDT historical backtest",
        experiment_description=(
            "Run registered Williams entry and exit rules on "
            "historical BTCUSDT data."
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
        entry_rule="williams_oversold_entry",
        exit_rule="stop_take_or_max_holding_exit",
        direction=MarketPositionDirection.LONG,
        stop_loss_percent=1.0,
        take_profit_percent=2.0,
        max_holding_bars=24,
        commission_percent=0.1,
        slippage_percent=0.05,
        strategy_parameters={
            "williams_period": 14,
            "oversold_level": -80,
        },
        tags=(
            "btc",
            "williams",
            "historical-backtest",
        ),
    )


def test_market_experiment_mapper_creates_linked_domain_objects() -> None:
    specification = build_specification()

    mapped = MarketExperimentMapper().map(specification)

    assert mapped.question.title == specification.question_title
    assert (
        mapped.question.description
        == specification.question_description
    )

    assert (
        mapped.hypothesis.question_id
        == mapped.question.id
    )
    assert (
        mapped.hypothesis.title
        == specification.hypothesis_title
    )
    assert (
        mapped.hypothesis.expected_result
        == specification.expected_result
    )

    assert (
        mapped.experiment.hypothesis_id
        == mapped.hypothesis.id
    )
    assert (
        mapped.experiment.title
        == specification.experiment_title
    )


def test_market_experiment_mapper_preserves_market_parameters() -> None:
    specification = build_specification()

    mapped = MarketExperimentMapper().map(specification)
    parameters = mapped.experiment.parameters

    assert parameters["executor_type"] == "market_backtest"
    assert parameters["data_source"] == "historical_csv"
    assert parameters["symbol"] == "BTCUSDT"
    assert parameters["timeframe"] == "1h"
    assert parameters["start_at"] == specification.start_at
    assert parameters["end_at"] == specification.end_at
    assert parameters["entry_rule"] == "williams_oversold_entry"
    assert (
        parameters["exit_rule"]
        == "stop_take_or_max_holding_exit"
    )
    assert parameters["direction"] == "LONG"
    assert parameters["stop_loss_percent"] == 1.0
    assert parameters["take_profit_percent"] == 2.0
    assert parameters["max_holding_bars"] == 24
    assert parameters["commission_percent"] == 0.1
    assert parameters["slippage_percent"] == 0.05
    assert parameters["strategy_parameters"] == {
        "williams_period": 14,
        "oversold_level": -80,
    }


def test_market_experiment_mapper_copies_mutable_values() -> None:
    specification = build_specification()

    mapped = MarketExperimentMapper().map(specification)

    mapped.experiment.tags.append("new-tag")
    mapped.experiment.parameters[
        "strategy_parameters"
    ]["williams_period"] = 7

    assert "new-tag" not in specification.tags
    assert (
        specification.strategy_parameters["williams_period"]
        == 14
    )