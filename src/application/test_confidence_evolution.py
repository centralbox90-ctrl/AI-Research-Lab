from src.application.confidence_evolution import (
    ConfidenceEvolution,
)


def test_confidence_evolution_creation():

    evolution = ConfidenceEvolution(
        previous_confidence=0.45,
        current_confidence=0.72,
        change_reason=(
            "Added out-of-sample validation"
        ),
    )

    assert (
        evolution.previous_confidence
        == 0.45
    )

    assert (
        evolution.current_confidence
        == 0.72
    )

    assert (
        evolution.change_reason
        == "Added out-of-sample validation"
    )