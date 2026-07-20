from dataclasses import replace
from datetime import datetime, timezone

import pytest

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


def test_market_experiment_mapper_maps_campaign() -> None:
    first_specification = build_specification()
    second_specification = replace(
        first_specification,
        experiment_title=(
            "Williams BTCUSDT four-hour historical backtest"
        ),
        experiment_description=(
            "Run the same Williams rules on four-hour "
            "historical BTCUSDT data."
        ),
        timeframe="4h",
    )

    mapped = MarketExperimentMapper().map_campaign(
        (
            first_specification,
            second_specification,
        )
    )

    assert mapped.question.title == (
        first_specification.question_title
    )
    assert mapped.hypothesis.question_id == mapped.question.id
    assert len(mapped.experiments) == 2

    assert (
        mapped.experiments[0].title
        == first_specification.experiment_title
    )
    assert (
        mapped.experiments[1].title
        == second_specification.experiment_title
    )
    assert mapped.experiments[0].parameters["timeframe"] == "1h"
    assert mapped.experiments[1].parameters["timeframe"] == "4h"


def test_market_experiment_mapper_campaign_shares_hypothesis() -> None:
    first_specification = build_specification()
    second_specification = replace(
        first_specification,
        experiment_title="Second Williams experiment",
        timeframe="4h",
    )

    mapped = MarketExperimentMapper().map_campaign(
        (
            first_specification,
            second_specification,
        )
    )

    assert all(
        experiment.hypothesis_id == mapped.hypothesis.id
        for experiment in mapped.experiments
    )


def test_market_experiment_mapper_rejects_empty_campaign() -> None:
    with pytest.raises(
        ValueError,
        match="must contain at least one",
    ):
        MarketExperimentMapper().map_campaign(())


def test_market_experiment_mapper_rejects_different_questions() -> None:
    first_specification = build_specification()
    second_specification = replace(
        first_specification,
        question_title="Does RSI oversold predict a rebound?",
        experiment_title="RSI historical backtest",
    )

    with pytest.raises(
        ValueError,
        match="same research question",
    ):
        MarketExperimentMapper().map_campaign(
            (
                first_specification,
                second_specification,
            )
        )


def test_market_experiment_mapper_rejects_different_hypotheses() -> None:
    first_specification = build_specification()
    second_specification = replace(
        first_specification,
        hypothesis_title=(
            "Williams oversold values do not precede "
            "positive returns"
        ),
        experiment_title="Alternative Williams experiment",
    )

    with pytest.raises(
        ValueError,
        match="same hypothesis",
    ):
        MarketExperimentMapper().map_campaign(
            (
                first_specification,
                second_specification,
            )
        )
