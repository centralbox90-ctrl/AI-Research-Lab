from src.application.evidence_metric_delta import (
    EvidenceMetricDelta,
)


def test_evidence_metric_delta_creation():

    delta = EvidenceMetricDelta(
        metric_name="net_profit",
        previous_value=-11.17,
        current_value=-8.64,
        absolute_delta=2.53,
        direction="increased",
    )

    assert delta.metric_name == "net_profit"
    assert delta.previous_value == -11.17
    assert delta.current_value == -8.64
    assert delta.absolute_delta == 2.53
    assert delta.direction == "increased"