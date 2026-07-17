from src.application.evidence_evolution import (
    EvidenceEvolution,
)
from src.application.evidence_metric_delta import (
    EvidenceMetricDelta,
)


def test_evidence_evolution_creation():

    metric_delta = EvidenceMetricDelta(
        metric_name="net_profit",
        previous_value=-11.17,
        current_value=-8.64,
        absolute_delta=2.53,
        direction="increased",
    )

    evolution = EvidenceEvolution(
        previous_evidence={
            "total_trades": 500,
            "markets": 1,
            "net_profit": -11.17,
        },
        current_evidence={
            "total_trades": 5000,
            "markets": 5,
            "net_profit": -8.64,
        },
        metric_deltas=[
            metric_delta,
        ],
        change_reason=(
            "Evidence changed between research artifacts."
        ),
    )

    assert evolution.previous_evidence == {
        "total_trades": 500,
        "markets": 1,
        "net_profit": -11.17,
    }

    assert evolution.current_evidence == {
        "total_trades": 5000,
        "markets": 5,
        "net_profit": -8.64,
    }

    assert evolution.metric_deltas == (
        metric_delta,
    )

    assert (
        evolution.change_reason
        == "Evidence changed between research artifacts."
    )