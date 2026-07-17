from src.research.experiment_evaluation import ExperimentEvaluation


def test_experiment_evaluation_stores_scientific_evaluation() -> None:
    evaluation = ExperimentEvaluation(
        experiment_id="experiment-1",
        is_valid=True,
        evidence_strength=0.75,
        warnings=["Limited sample size"],
        notes="Requires robustness evaluation",
    )

    assert evaluation.experiment_id == "experiment-1"
    assert evaluation.is_valid is True
    assert evaluation.evidence_strength == 0.75
    assert evaluation.warnings == ["Limited sample size"]
    assert evaluation.notes == "Requires robustness evaluation"