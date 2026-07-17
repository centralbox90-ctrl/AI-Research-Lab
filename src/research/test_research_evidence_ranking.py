import pytest

from src.research.engine import ResearchEngine
from src.research.experiment import Experiment
from src.research.experiment_result import ExperimentResult
from src.research.hypothesis import Hypothesis
from src.research.question import Question
from src.research.research_types import ExperimentStatus


def test_research_engine_runs_many_and_ranks_evidence() -> None:
    question = Question(
        title="Evidence ranking research",
    )

    hypothesis = Hypothesis(
        question_id=question.id,
        title="Experiment returns are consistently positive",
    )

    strong_experiment = Experiment(
        hypothesis_id=hypothesis.id,
        title="Strong evidence experiment",
        parameters={"scenario": "strong"},
    )

    moderate_experiment = Experiment(
        hypothesis_id=hypothesis.id,
        title="Moderate evidence experiment",
        parameters={"scenario": "moderate"},
    )

    weak_experiment = Experiment(
        hypothesis_id=hypothesis.id,
        title="Weak evidence experiment",
        parameters={"scenario": "weak"},
    )

    experiments = [
        moderate_experiment,
        weak_experiment,
        strong_experiment,
    ]

    observations_by_scenario = {
        "strong": [1.8, 2.0, 2.1, 1.9, 2.2],
        "moderate": [1.0, -0.5, 2.0, 1.5],
        "weak": [2.0, 1.0, -1.0, -2.0],
    }

    def execute(current_experiment: Experiment) -> ExperimentResult:
        scenario = current_experiment.parameters["scenario"]
        observations = observations_by_scenario[scenario]

        return ExperimentResult(
            experiment_id=current_experiment.id,
            success=True,
            metrics={
                "net_profit": float(sum(observations)),
                "total_trades": len(observations),
            },
            observations={
                "profit_percent": observations,
            },
            conclusion=(
                f"Completed {scenario} evidence experiment"
            ),
        )

    cycles, ranked_evidence = (
        ResearchEngine().run_many_and_rank_evidence(
            question=question,
            hypothesis=hypothesis,
            experiments=experiments,
            executor=execute,
        )
    )

    assert len(cycles) == 3
    assert len(ranked_evidence) == 3

    for experiment in experiments:
        assert experiment.status == ExperimentStatus.COMPLETED

    moderate_cycle = cycles[0]
    weak_cycle = cycles[1]
    strong_cycle = cycles[2]

    assert (
        moderate_cycle.result.experiment_id
        == moderate_experiment.id
    )
    assert weak_cycle.result.experiment_id == weak_experiment.id
    assert strong_cycle.result.experiment_id == strong_experiment.id

    moderate_evidence_strength = (
        moderate_cycle.evidence_strength_evaluation
    )
    weak_evidence_strength = (
        weak_cycle.evidence_strength_evaluation
    )
    strong_evidence_strength = (
        strong_cycle.evidence_strength_evaluation
    )

    assert moderate_evidence_strength.is_evaluated is True
    assert weak_evidence_strength.is_evaluated is True
    assert strong_evidence_strength.is_evaluated is True

    assert (
        strong_evidence_strength.score
        > moderate_evidence_strength.score
    )
    assert (
        moderate_evidence_strength.score
        > weak_evidence_strength.score
    )

    assert strong_evidence_strength.level == "very_strong"
    assert moderate_evidence_strength.level == "strong"
    assert weak_evidence_strength.level == "weak"

    assert ranked_evidence[0].rank == 1
    assert ranked_evidence[0].experiment == strong_experiment
    assert (
        ranked_evidence[0].evidence_strength_evaluation
        == strong_evidence_strength
    )
    assert ranked_evidence[0].score == pytest.approx(
        strong_evidence_strength.score
    )
    assert ranked_evidence[0].level == "very_strong"

    assert ranked_evidence[1].rank == 2
    assert ranked_evidence[1].experiment == moderate_experiment
    assert (
        ranked_evidence[1].evidence_strength_evaluation
        == moderate_evidence_strength
    )
    assert ranked_evidence[1].score == pytest.approx(
        moderate_evidence_strength.score
    )
    assert ranked_evidence[1].level == "strong"

    assert ranked_evidence[2].rank == 3
    assert ranked_evidence[2].experiment == weak_experiment
    assert (
        ranked_evidence[2].evidence_strength_evaluation
        == weak_evidence_strength
    )
    assert ranked_evidence[2].score == pytest.approx(
        weak_evidence_strength.score
    )
    assert ranked_evidence[2].level == "weak"

    assert ranked_evidence[0].warnings == []
    assert ranked_evidence[1].warnings == []
    assert ranked_evidence[2].warnings == []

    assert strong_cycle.hypothesis_decision.is_supported is True
    assert moderate_cycle.hypothesis_decision.is_supported is False
    assert weak_cycle.hypothesis_decision.is_supported is False

    assert strong_cycle.analysis.findings[
        "evidence_strength_score"
    ] == pytest.approx(strong_evidence_strength.score)

    assert moderate_cycle.analysis.findings[
        "evidence_strength_score"
    ] == pytest.approx(moderate_evidence_strength.score)

    assert weak_cycle.analysis.findings[
        "evidence_strength_score"
    ] == pytest.approx(weak_evidence_strength.score)

    assert strong_cycle.conclusion.supported is True
    assert moderate_cycle.conclusion.supported is False
    assert weak_cycle.conclusion.supported is False

    assert strong_cycle.conclusion.is_provisional is False
    assert moderate_cycle.conclusion.is_provisional is False
    assert weak_cycle.conclusion.is_provisional is False