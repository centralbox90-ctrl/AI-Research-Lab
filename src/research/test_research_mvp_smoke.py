from src.research import (
    Experiment,
    ExperimentResult,
    Hypothesis,
    NextExperimentResearchCycleResult,
    Question,
    ResearchEngine,
)


def test_research_mvp_complete_pipeline_smoke() -> None:
    question = Question(
        title="Can the observed effect be supported?",
    )

    hypothesis = Hypothesis(
        question_id=question.id,
        title="The observed effect is consistently positive",
    )

    experiment = Experiment(
        hypothesis_id=hypothesis.id,
        title="MVP scientific experiment",
    )

    def execute(current_experiment: Experiment) -> ExperimentResult:
        return ExperimentResult(
            experiment_id=current_experiment.id,
            success=True,
            metrics={
                "net_profit": 10.0,
                "total_trades": 5,
            },
            observations={
                "profit_percent": [
                    1.8,
                    2.0,
                    2.1,
                    1.9,
                    2.2,
                ],
            },
            conclusion="A stable positive effect was observed.",
        )

    cycle = ResearchEngine().run_with_next_experiment_selection(
        question=question,
        hypothesis=hypothesis,
        experiment=experiment,
        executor=execute,
    )

    assert isinstance(
        cycle,
        NextExperimentResearchCycleResult,
    )

    assert cycle.result.success is True
    assert cycle.evaluation.is_valid is True

    assert cycle.statistical_evaluation.is_evaluated is True
    assert cycle.statistical_evaluation.is_significant is True

    assert cycle.robustness_evaluation.is_evaluated is True
    assert cycle.robustness_evaluation.is_robust is True

    assert cycle.contradiction_evaluation.is_evaluated is True
    assert cycle.contradiction_evaluation.has_contradiction is False

    assert cycle.evidence_strength_evaluation.is_evaluated is True
    assert cycle.evidence_strength_evaluation.level == "very_strong"

    assert cycle.hypothesis_decision.is_evaluated is True
    assert cycle.hypothesis_decision.is_supported is True

    assert cycle.next_experiment_selection.is_selected is True
    assert (
        cycle.next_experiment_selection.action
        == "replicate_experiment"
    )
    assert (
        cycle.next_experiment_selection.target_requirement
        == "independent_replication"
    )

    assert cycle.evidence.data == cycle.result.metrics

    assert cycle.analysis.findings[
        "hypothesis_supported"
    ] is True

    assert cycle.analysis.findings[
        "next_experiment_action"
    ] == "replicate_experiment"

    assert cycle.conclusion.supported is True
    assert cycle.conclusion.is_provisional is False

    assert cycle.knowledge.is_provisional is False
    assert cycle.knowledge.statement == cycle.conclusion.statement

    assert len(cycle) == 12