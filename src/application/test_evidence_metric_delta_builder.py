import pytest

from src.application.evidence_metric_delta_builder import (
    EvidenceMetricDeltaBuilder,
)


def test_evidence_metric_delta_builder():

    builder = EvidenceMetricDeltaBuilder()

    deltas = builder.build(
        previous_evidence={
            "net_profit": -11.17,
            "win_rate": 35.71,
            "total_trades": 42,
            "market": "BTCUSDT",
            "removed_metric": 10,
        },
        current_evidence={
            "net_profit": -8.64,
            "win_rate": 33.33,
            "total_trades": 42,
            "market": "ETHUSDT",
            "added_metric": 20,
        },
    )

    by_name = {
        delta.metric_name: delta
        for delta in deltas
    }

    assert by_name["net_profit"].direction == "increased"
    assert by_name["net_profit"].absolute_delta == pytest.approx(
        2.53
    )

    assert by_name["win_rate"].direction == "decreased"
    assert by_name["win_rate"].absolute_delta == pytest.approx(
        -2.38
    )

    assert by_name["total_trades"].direction == "unchanged"
    assert by_name["total_trades"].absolute_delta == 0.0

    assert by_name["market"].direction == "not_comparable"
    assert by_name["market"].absolute_delta is None

    assert by_name["added_metric"].direction == "added"
    assert by_name["added_metric"].previous_value is None

    assert by_name["removed_metric"].direction == "removed"
    assert by_name["removed_metric"].current_value is None