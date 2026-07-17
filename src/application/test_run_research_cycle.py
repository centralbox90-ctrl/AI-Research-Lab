from src.application import RunResearchCycle
from src.research import (
    Experiment,
    ExperimentResult,
    Hypothesis,
    NextExperimentResearchCycleResult,
    Question,
    ResearchEngine,
)


class RecordingResearchEngine(ResearchEngine):
    def __init__(self) -> None:
        super().__init__()
        self.received_question: Question | None = None
        self.received_hypothesis: Hypothesis | None = None
        self.received_experiment: Experiment | None = None

    def run_with_next_experiment_selection(
        self,
        question: Question,
        hypothesis: Hypothesis,
        experiment: Experiment,
        executor,
    ) -> NextExperimentResearchCycleResult:
        self.received_question = question
        self.received_hypothesis = hypothesis
        self.received_experiment = experiment

        return super().run_with_next_experiment_selection(
            question=question,
            hypothesis=hypothesis,
            experiment=experiment,
            executor=executor,
        )


def test_run_research_cycle_executes_complete_research_pipeline() -> None:
    question = Question(
        title="Can the application layer run a research cycle?",
    )

    hypothesis = Hypothesis(
        question_id=question.id,
        title="The complete research pipeline can be invoked as a use case",
    )

    experiment = Experiment(
        hypothesis_id=hypothesis.id,
        title="Application-layer research experiment",
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

    research_engine = RecordingResearchEngine()
    use_case = RunResearchCycle(research_engine=research_engine)

    cycle = use_case.execute(
        question=question,
        hypothesis=hypothesis,
        experiment=experiment,
        executor=execute,
    )

    assert isinstance(cycle, NextExperimentResearchCycleResult)

    assert research_engine.received_question is question
    assert research_engine.received_hypothesis is hypothesis
    assert research_engine.received_experiment is experiment

    assert cycle.result.success is True
    assert cycle.evidence_strength_evaluation.level == "very_strong"
    assert cycle.hypothesis_decision.is_supported is True

    assert (
        cycle.next_experiment_selection.action
        == "replicate_experiment"
    )
    assert (
        cycle.next_experiment_selection.target_requirement
        == "independent_replication"
    )

    assert cycle.conclusion.supported is True
    assert cycle.knowledge.is_provisional is False

    result, *_ = cycle
    assert result is cycle.result
    assert len(cycle) == 12