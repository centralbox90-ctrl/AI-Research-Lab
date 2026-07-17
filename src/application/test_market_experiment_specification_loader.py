import json
from datetime import timezone
from pathlib import Path

import pytest

from src.application import (
    MarketExperimentSpecificationLoader,
    MarketPositionDirection,
)


def build_payload() -> dict[str, object]:
    return {
        "executor_type": "market_backtest",
        "question_title": (
            "Does Williams oversold predict a rebound?"
        ),
        "question_description": (
            "Test whether a Williams oversold condition is followed "
            "by positive historical trade returns."
        ),
        "hypothesis_title": (
            "Williams oversold values precede positive returns"
        ),
        "hypothesis_description": (
            "BTCUSDT should produce positive trade results after "
            "the registered Williams oversold condition."
        ),
        "expected_result": (
            "Positive net profit with a non-zero number of trades."
        ),
        "experiment_title": (
            "Williams BTCUSDT historical backtest"
        ),
        "experiment_description": (
            "Run registered entry and exit rules on historical data."
        ),
        "data_source": "historical_csv",
        "symbol": "BTCUSDT",
        "timeframe": "1h",
        "start_at": "2024-01-01T00:00:00Z",
        "end_at": "2024-12-31T00:00:00+00:00",
        "entry_rule": "williams_oversold_entry",
        "exit_rule": "stop_take_or_max_holding_exit",
        "direction": "LONG",
        "stop_loss_percent": 1.0,
        "take_profit_percent": 2.0,
        "max_holding_bars": 24,
        "commission_percent": 0.1,
        "slippage_percent": 0.05,
        "strategy_parameters": {
            "williams_period": 14,
            "oversold_level": -80,
        },
        "tags": [
            "btc",
            "williams",
            "historical-backtest",
        ],
    }


def test_loader_creates_specification_from_dictionary() -> None:
    specification = (
        MarketExperimentSpecificationLoader().from_dict(
            build_payload(),
        )
    )

    assert specification.executor_type == "market_backtest"
    assert specification.symbol == "BTCUSDT"
    assert specification.direction is MarketPositionDirection.LONG

    assert specification.start_at.tzinfo is timezone.utc
    assert specification.end_at.tzinfo is not None

    assert specification.strategy_parameters == {
        "williams_period": 14,
        "oversold_level": -80,
    }

    assert specification.tags == (
        "btc",
        "williams",
        "historical-backtest",
    )


def test_loader_reads_utf8_json_file(
    tmp_path: Path,
) -> None:
    payload = build_payload()
    payload["question_title"] = (
        "Предсказывает ли перепроданность рост?"
    )

    specification_path = tmp_path / "experiment.json"
    specification_path.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    specification = (
        MarketExperimentSpecificationLoader().load(
            specification_path,
        )
    )

    assert specification.question_title == (
        "Предсказывает ли перепроданность рост?"
    )


def test_loader_rejects_invalid_json(
    tmp_path: Path,
) -> None:
    specification_path = tmp_path / "experiment.json"
    specification_path.write_text(
        "{invalid-json",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="invalid specification JSON",
    ):
        MarketExperimentSpecificationLoader().load(
            specification_path,
        )


def test_loader_rejects_non_object_json() -> None:
    with pytest.raises(
        ValueError,
        match="specification JSON must contain an object",
    ):
        MarketExperimentSpecificationLoader().from_dict(
            ["market_backtest"],
        )


def test_loader_rejects_missing_required_field() -> None:
    payload = build_payload()
    del payload["symbol"]

    with pytest.raises(
        ValueError,
        match="missing specification fields: symbol",
    ):
        MarketExperimentSpecificationLoader().from_dict(
            payload,
        )


def test_loader_rejects_unknown_field() -> None:
    payload = build_payload()
    payload["python_callable"] = "package.module:function"

    with pytest.raises(
        ValueError,
        match=(
            "unknown specification fields: python_callable"
        ),
    ):
        MarketExperimentSpecificationLoader().from_dict(
            payload,
        )


def test_loader_rejects_invalid_datetime() -> None:
    payload = build_payload()
    payload["start_at"] = "not-a-datetime"

    with pytest.raises(
        ValueError,
        match=(
            "start_at must be a valid ISO 8601 datetime"
        ),
    ):
        MarketExperimentSpecificationLoader().from_dict(
            payload,
        )


def test_loader_rejects_invalid_direction() -> None:
    payload = build_payload()
    payload["direction"] = "BOTH"

    with pytest.raises(
        ValueError,
        match="direction must be 'LONG' or 'SHORT'",
    ):
        MarketExperimentSpecificationLoader().from_dict(
            payload,
        )


def test_loader_rejects_non_object_strategy_parameters() -> None:
    payload = build_payload()
    payload["strategy_parameters"] = [
        "williams_period",
        14,
    ]

    with pytest.raises(
        ValueError,
        match="strategy_parameters must be an object",
    ):
        MarketExperimentSpecificationLoader().from_dict(
            payload,
        )


def test_loader_rejects_non_array_tags() -> None:
    payload = build_payload()
    payload["tags"] = "btc"

    with pytest.raises(
        ValueError,
        match="tags must be an array",
    ):
        MarketExperimentSpecificationLoader().from_dict(
            payload,
        )