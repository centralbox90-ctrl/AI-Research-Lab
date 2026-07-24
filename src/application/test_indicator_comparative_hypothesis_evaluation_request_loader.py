import json
from pathlib import Path

import pytest

from src.application.indicator_comparative_hypothesis_evaluation_application import (
    IndicatorComparativeFindingRequest,
)
from src.application.indicator_comparative_hypothesis_evaluation_request_loader import (
    IndicatorComparativeHypothesisEvaluationRequest,
    IndicatorComparativeHypothesisEvaluationRequestLoader,
)
from src.application.market_experiment_specification import (
    MarketPositionDirection,
)


def build_market_specification_payload(
) -> dict[str, object]:
    return {
        "executor_type": "market_backtest",
        "question_title": "Does RSI predict returns?",
        "question_description": (
            "Evaluate RSI across replicated markets."
        ),
        "hypothesis_title": (
            "RSI oversold values precede positive returns"
        ),
        "hypothesis_description": (
            "Replicated RSI observations should "
            "support positive forward returns."
        ),
        "expected_result": (
            "Positive comparative evidence."
        ),
        "experiment_title": (
            "RSI comparative experiment"
        ),
        "experiment_description": (
            "Run the declared RSI experiment."
        ),
        "data_source": "generated",
        "symbol": "EURUSD",
        "timeframe": "H1",
        "start_at": "2026-01-01T00:00:00Z",
        "end_at": "2026-02-01T00:00:00Z",
        "entry_rule": "rsi < 30",
        "exit_rule": "rsi > 50",
        "direction": "LONG",
        "stop_loss_percent": 1.0,
        "take_profit_percent": 2.0,
        "max_holding_bars": 10,
    }


def build_payload() -> dict[str, object]:
    return {
        "hypothesis_id": " hypothesis-rsi ",
        "requests": [
            {
                "market_specifications": [
                    build_market_specification_payload(),
                ],
                "indicator_id": " rsi ",
                "outcome_specification": {
                    "horizons": [1, 3],
                    "price_field": " close ",
                },
                "horizon": 3,
                "statement": (
                    " RSI supports positive returns. "
                ),
                "applicable_markets": [
                    "EURUSD:H1",
                ],
            },
        ],
    }


def test_loader_creates_typed_request_from_dictionary(
) -> None:
    loaded = (
        IndicatorComparativeHypothesisEvaluationRequestLoader()
        .from_dict(build_payload())
    )

    assert isinstance(
        loaded,
        IndicatorComparativeHypothesisEvaluationRequest,
    )
    assert loaded.hypothesis_id == "hypothesis-rsi"
    assert len(loaded.requests) == 1

    request = loaded.requests[0]

    assert isinstance(
        request,
        IndicatorComparativeFindingRequest,
    )
    assert request.indicator_id == "rsi"
    assert request.horizon == 3
    assert request.outcome_specification.horizons == (
        1,
        3,
    )
    assert (
        request.outcome_specification.price_field
        == "close"
    )
    assert request.applicable_markets == (
        "EURUSD:H1",
    )
    assert (
        request.market_specifications[0].direction
        is MarketPositionDirection.LONG
    )


def test_loader_reads_utf8_json_file(
    tmp_path: Path,
) -> None:
    request_path = tmp_path / "evaluation.json"
    payload = build_payload()
    payload["requests"][0]["statement"] = (
        "Индикатор подтверждает гипотезу."
    )
    request_path.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    loaded = (
        IndicatorComparativeHypothesisEvaluationRequestLoader()
        .load(request_path)
    )

    assert loaded.requests[0].statement == (
        "Индикатор подтверждает гипотезу."
    )


def test_loader_rejects_invalid_json(
    tmp_path: Path,
) -> None:
    request_path = tmp_path / "invalid.json"
    request_path.write_text(
        "{invalid-json",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="invalid comparative evaluation JSON",
    ):
        (
            IndicatorComparativeHypothesisEvaluationRequestLoader()
            .load(request_path)
        )


def test_loader_rejects_non_object_json() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "comparative evaluation JSON must "
            "contain an object"
        ),
    ):
        (
            IndicatorComparativeHypothesisEvaluationRequestLoader()
            .from_dict([])
        )


def test_loader_rejects_missing_outer_field(
) -> None:
    payload = build_payload()
    del payload["hypothesis_id"]

    with pytest.raises(
        ValueError,
        match=(
            "comparative evaluation request "
            "missing fields: hypothesis_id"
        ),
    ):
        (
            IndicatorComparativeHypothesisEvaluationRequestLoader()
            .from_dict(payload)
        )


def test_loader_rejects_unknown_outer_field(
) -> None:
    payload = build_payload()
    payload["callback"] = "package.module:function"

    with pytest.raises(
        ValueError,
        match=(
            "comparative evaluation request "
            "unknown fields: callback"
        ),
    ):
        (
            IndicatorComparativeHypothesisEvaluationRequestLoader()
            .from_dict(payload)
        )


@pytest.mark.parametrize(
    "requests",
    (
        "not-an-array",
        [],
    ),
)
def test_loader_rejects_invalid_requests_collection(
    requests: object,
) -> None:
    payload = build_payload()
    payload["requests"] = requests

    with pytest.raises(
        ValueError,
        match="requests must",
    ):
        (
            IndicatorComparativeHypothesisEvaluationRequestLoader()
            .from_dict(payload)
        )


def test_loader_rejects_unknown_nested_field(
) -> None:
    payload = build_payload()
    payload["requests"][0]["runtime_hook"] = "unsafe"

    with pytest.raises(
        ValueError,
        match=(
            r"requests\[0\] unknown fields: runtime_hook"
        ),
    ):
        (
            IndicatorComparativeHypothesisEvaluationRequestLoader()
            .from_dict(payload)
        )


def test_loader_rejects_non_array_horizons(
) -> None:
    payload = build_payload()
    payload["requests"][0][
        "outcome_specification"
    ]["horizons"] = "1,3"

    with pytest.raises(
        ValueError,
        match="horizons must be an array",
    ):
        (
            IndicatorComparativeHypothesisEvaluationRequestLoader()
            .from_dict(payload)
        )


def test_loader_rejects_undeclared_selected_horizon(
) -> None:
    payload = build_payload()
    payload["requests"][0]["horizon"] = 5

    with pytest.raises(
        ValueError,
        match=(
            "horizon must be declared in "
            "outcome_specification"
        ),
    ):
        (
            IndicatorComparativeHypothesisEvaluationRequestLoader()
            .from_dict(payload)
        )


def test_loader_rejects_non_array_market_collections(
) -> None:
    payload = build_payload()
    payload["requests"][0][
        "applicable_markets"
    ] = "EURUSD:H1"

    with pytest.raises(
        ValueError,
        match="applicable_markets must be an array",
    ):
        (
            IndicatorComparativeHypothesisEvaluationRequestLoader()
            .from_dict(payload)
        )