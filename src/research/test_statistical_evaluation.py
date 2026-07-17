from src.research.statistical_evaluation import StatisticalEvaluation


def test_statistical_evaluation_stores_analysis_results() -> None:
    evaluation = StatisticalEvaluation(
        experiment_id="experiment-1",
        is_evaluated=True,
        is_significant=True,
        p_value=0.03,
        effect_size=0.42,
        confidence_level=0.95,
        sample_size=250,
        warnings=["Multiple testing correction is not applied"],
        notes="Preliminary statistical evaluation",
    )

    assert evaluation.experiment_id == "experiment-1"
    assert evaluation.is_evaluated is True
    assert evaluation.is_significant is True
    assert evaluation.p_value == 0.03
    assert evaluation.effect_size == 0.42
    assert evaluation.confidence_level == 0.95
    assert evaluation.sample_size == 250
    assert evaluation.warnings == [
        "Multiple testing correction is not applied"
    ]
    assert evaluation.notes == "Preliminary statistical evaluation"