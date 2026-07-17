from src.research.experiment_evaluator import ExperimentEvaluator
from src.research.experiment_result import ExperimentResult


def test_experiment_evaluator_accepts_valid_result() -> None:
    result = ExperimentResult(
        experiment_id="experiment-1",
        metrics={
            "net_profit": 8.0,
            "win_rate": 61.0,
        },
    )

    evaluation = ExperimentEvaluator().evaluate(result)

    assert evaluation.experiment_id == "experiment-1"
    assert evaluation.is_valid is True
    assert evaluation.evidence_strength == 0.0
    assert evaluation.warnings == []
    assert (
        evaluation.notes
        == (
            "Result passed basic validation. "
            "Statistical and robustness evaluation are not implemented."
        )
    )


def test_experiment_evaluator_rejects_invalid_result() -> None:
    result = ExperimentResult(
        experiment_id="",
        metrics={
            "net_profit": float("nan"),
            "label": "profitable",
        },
    )

    evaluation = ExperimentEvaluator().evaluate(result)

    assert evaluation.is_valid is False
    assert evaluation.evidence_strength == 0.0
    assert evaluation.warnings == [
        "Experiment ID is missing",
        "Metric 'net_profit' is not finite",
        "Metric 'label' is not numeric",
    ]
    assert evaluation.notes == "Result failed basic validation."