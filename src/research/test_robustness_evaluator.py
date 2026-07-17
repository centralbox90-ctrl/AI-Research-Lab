import pytest

from src.research.experiment_result import ExperimentResult
from src.research.robustness_evaluator import RobustnessEvaluator


def test_robustness_evaluator_requires_raw_observations() -> None:
    result = ExperimentResult(
        experiment_id="experiment-1",
        metrics={"net_profit": 8.0},
    )

    evaluation = RobustnessEvaluator().evaluate(result)

    assert evaluation.experiment_id == "experiment-1"
    assert evaluation.is_evaluated is False
    assert evaluation.is_robust is False

    assert evaluation.sample_size is None
    assert evaluation.positive_observation_ratio is None
    assert evaluation.negative_observation_ratio is None
    assert evaluation.zero_observation_ratio is None

    assert "Raw observations are missing" in evaluation.warnings
    assert (
        evaluation.notes
        == (
            "Robustness evaluation requires raw observations. "
            "Aggregate metrics are insufficient."
        )
    )


def test_robustness_evaluator_detects_robust_result() -> None:
    result = ExperimentResult(
        experiment_id="experiment-1",
        metrics={"net_profit": 3.0},
    )

    evaluation = RobustnessEvaluator().evaluate(
        result=result,
        observations=[1.0, -0.5, 2.0, 1.5],
    )

    assert evaluation.experiment_id == "experiment-1"
    assert evaluation.is_evaluated is True
    assert evaluation.is_robust is True
    assert evaluation.sample_size == 4

    assert evaluation.positive_observation_ratio == pytest.approx(0.75)
    assert evaluation.negative_observation_ratio == pytest.approx(0.25)
    assert evaluation.zero_observation_ratio == pytest.approx(0.0)

    assert evaluation.first_half_mean == pytest.approx(0.25)
    assert evaluation.second_half_mean == pytest.approx(1.75)
    assert evaluation.mean_shift == pytest.approx(1.5)
    assert evaluation.direction_consistent is True

    assert evaluation.warnings == []
    assert (
        evaluation.notes
        == (
            "Direction ratios and split-sample diagnostics were "
            "calculated. Robustness was evaluated using direction "
            "consistency and the dominant observation direction ratio."
        )
    )


def test_robustness_evaluator_detects_direction_change() -> None:
    result = ExperimentResult(
        experiment_id="experiment-1",
        metrics={"net_profit": 0.0},
        observations={
            "profit_percent": [2.0, 1.0, -1.0, -2.0],
        },
    )

    evaluation = RobustnessEvaluator().evaluate(result)

    assert evaluation.is_evaluated is True
    assert evaluation.is_robust is False
    assert evaluation.sample_size == 4

    assert evaluation.positive_observation_ratio == pytest.approx(0.5)
    assert evaluation.negative_observation_ratio == pytest.approx(0.5)
    assert evaluation.zero_observation_ratio == pytest.approx(0.0)

    assert evaluation.first_half_mean == pytest.approx(1.5)
    assert evaluation.second_half_mean == pytest.approx(-1.5)
    assert evaluation.mean_shift == pytest.approx(-3.0)
    assert evaluation.direction_consistent is False


def test_robustness_evaluator_rejects_weak_dominant_direction() -> None:
    result = ExperimentResult(
        experiment_id="experiment-1",
        metrics={"net_profit": 1.0},
    )

    evaluation = RobustnessEvaluator().evaluate(
        result=result,
        observations=[2.0, -1.0, 2.0, -1.0],
    )

    assert evaluation.is_evaluated is True
    assert evaluation.is_robust is False
    assert evaluation.sample_size == 4

    assert evaluation.positive_observation_ratio == pytest.approx(0.5)
    assert evaluation.negative_observation_ratio == pytest.approx(0.5)
    assert evaluation.zero_observation_ratio == pytest.approx(0.0)

    assert evaluation.first_half_mean == pytest.approx(0.5)
    assert evaluation.second_half_mean == pytest.approx(0.5)
    assert evaluation.direction_consistent is True


def test_robustness_evaluator_handles_single_observation() -> None:
    result = ExperimentResult(
        experiment_id="experiment-1",
        metrics={"net_profit": 1.0},
    )

    evaluation = RobustnessEvaluator().evaluate(
        result=result,
        observations=[1.0],
    )

    assert evaluation.is_evaluated is True
    assert evaluation.is_robust is False
    assert evaluation.sample_size == 1

    assert evaluation.positive_observation_ratio == pytest.approx(1.0)
    assert evaluation.negative_observation_ratio == pytest.approx(0.0)
    assert evaluation.zero_observation_ratio == pytest.approx(0.0)

    assert evaluation.first_half_mean is None
    assert evaluation.second_half_mean is None
    assert evaluation.mean_shift is None
    assert evaluation.direction_consistent is None

    assert (
        "At least two numeric observations are required "
        "for split-sample diagnostics and robustness decision"
    ) in evaluation.warnings

    assert (
        evaluation.notes
        == (
            "Observation direction ratios were calculated. "
            "Split-sample diagnostics and robustness decision "
            "require at least two observations."
        )
    )