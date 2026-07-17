import pytest

from src.research.evidence_strength_evaluation import (
    EvidenceStrengthEvaluation,
)
from src.research.evidence_strength_ranker import (
    EvidenceStrengthRanker,
)
from src.research.experiment import Experiment


def test_evidence_strength_ranker_sorts_by_score() -> None:
    experiment_1 = Experiment(title="Experiment 1")
    experiment_2 = Experiment(title="Experiment 2")
    experiment_3 = Experiment(title="Experiment 3")

    evaluation_1 = EvidenceStrengthEvaluation(
        experiment_id=experiment_1.id,
        is_evaluated=True,
        score=0.50,
        level="moderate",
    )

    evaluation_2 = EvidenceStrengthEvaluation(
        experiment_id=experiment_2.id,
        is_evaluated=True,
        score=0.95,
        level="very_strong",
    )

    evaluation_3 = EvidenceStrengthEvaluation(
        experiment_id=experiment_3.id,
        is_evaluated=True,
        score=0.80,
        level="strong",
    )

    ranked = EvidenceStrengthRanker().rank(
        experiments=[
            experiment_1,
            experiment_2,
            experiment_3,
        ],
        evaluations=[
            evaluation_1,
            evaluation_2,
            evaluation_3,
        ],
    )

    assert len(ranked) == 3

    assert ranked[0].rank == 1
    assert ranked[0].experiment == experiment_2
    assert ranked[0].evidence_strength_evaluation == evaluation_2
    assert ranked[0].score == pytest.approx(0.95)
    assert ranked[0].level == "very_strong"

    assert ranked[1].rank == 2
    assert ranked[1].experiment == experiment_3
    assert ranked[1].score == pytest.approx(0.80)
    assert ranked[1].level == "strong"

    assert ranked[2].rank == 3
    assert ranked[2].experiment == experiment_1
    assert ranked[2].score == pytest.approx(0.50)
    assert ranked[2].level == "moderate"


def test_evidence_strength_ranker_places_incomplete_evaluation_last() -> None:
    completed_experiment = Experiment(
        title="Completed evidence experiment",
    )
    incomplete_experiment = Experiment(
        title="Incomplete evidence experiment",
    )

    completed_evaluation = EvidenceStrengthEvaluation(
        experiment_id=completed_experiment.id,
        is_evaluated=True,
        score=0.40,
        level="weak",
    )

    incomplete_evaluation = EvidenceStrengthEvaluation(
        experiment_id=incomplete_experiment.id,
        is_evaluated=False,
        score=1.0,
        level="unknown",
    )

    ranked = EvidenceStrengthRanker().rank(
        experiments=[
            incomplete_experiment,
            completed_experiment,
        ],
        evaluations=[
            incomplete_evaluation,
            completed_evaluation,
        ],
    )

    assert ranked[0].experiment == completed_experiment
    assert ranked[0].rank == 1
    assert ranked[0].score == pytest.approx(0.40)

    assert ranked[1].experiment == incomplete_experiment
    assert ranked[1].rank == 2
    assert ranked[1].score == pytest.approx(1.0)


def test_evidence_strength_ranker_preserves_mismatch_warning() -> None:
    experiment = Experiment(
        title="Experiment",
    )

    evaluation = EvidenceStrengthEvaluation(
        experiment_id="different-experiment",
        is_evaluated=True,
        score=0.75,
        level="strong",
        warnings=["Existing warning"],
    )

    ranked = EvidenceStrengthRanker().rank(
        experiments=[experiment],
        evaluations=[evaluation],
    )

    assert len(ranked) == 1

    assert ranked[0].warnings == [
        "Existing warning",
        "Evidence evaluation belongs to a different experiment",
    ]


def test_evidence_strength_ranker_requires_equal_lengths() -> None:
    experiment = Experiment(
        title="Experiment",
    )

    with pytest.raises(
        ValueError,
        match=(
            "Experiments and evidence evaluations must have "
            "the same length"
        ),
    ):
        EvidenceStrengthRanker().rank(
            experiments=[experiment],
            evaluations=[],
        )


def test_evidence_strength_ranker_returns_best_evidence() -> None:
    experiment_1 = Experiment(title="Experiment 1")
    experiment_2 = Experiment(title="Experiment 2")

    evaluation_1 = EvidenceStrengthEvaluation(
        experiment_id=experiment_1.id,
        is_evaluated=True,
        score=0.60,
        level="moderate",
    )

    evaluation_2 = EvidenceStrengthEvaluation(
        experiment_id=experiment_2.id,
        is_evaluated=True,
        score=0.90,
        level="very_strong",
    )

    best = EvidenceStrengthRanker().best(
        experiments=[
            experiment_1,
            experiment_2,
        ],
        evaluations=[
            evaluation_1,
            evaluation_2,
        ],
    )

    assert best.rank == 1
    assert best.experiment == experiment_2
    assert best.evidence_strength_evaluation == evaluation_2
    assert best.score == pytest.approx(0.90)
    assert best.level == "very_strong"


def test_evidence_strength_ranker_best_requires_items() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "At least one experiment and evidence evaluation "
            "are required"
        ),
    ):
        EvidenceStrengthRanker().best(
            experiments=[],
            evaluations=[],
        )