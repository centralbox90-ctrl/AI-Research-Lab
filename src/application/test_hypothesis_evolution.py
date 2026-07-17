from src.application.hypothesis_evolution import (
    HypothesisEvolution,
)


def test_hypothesis_evolution_creation():

    evolution = HypothesisEvolution(
        previous_hypothesis=(
            "Williams predicts reversal"
        ),
        current_hypothesis=(
            "Williams plus ADX predicts reversal"
        ),
        change_reason=(
            "Added trend confirmation"
        ),
    )

    assert (
        evolution.previous_hypothesis
        == "Williams predicts reversal"
    )

    assert (
        evolution.current_hypothesis
        == "Williams plus ADX predicts reversal"
    )

    assert (
        evolution.change_reason
        == "Added trend confirmation"
    )