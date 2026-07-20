from datetime import datetime
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from src.research.ai_scientist import AIScientist
from src.research.experiment import Experiment
from src.research.research_execution import ResearchExecution
from src.research.research_campaign import ResearchCampaign

def test_ai_scientist_defaults() -> None:
    scientist = AIScientist()

    assert scientist.name == "AI Scientist"
    assert scientist.executions == []


def test_start_execution() -> None:
    scientist = AIScientist()
    execution = ResearchExecution()

    scientist.start_execution(execution)

    assert scientist.total_executions() == 1
    assert scientist.executions[0] is execution


def test_completed_executions() -> None:
    scientist = AIScientist()

    scientist.start_execution(ResearchExecution())

    scientist.start_execution(
        ResearchExecution(
            completed_at=datetime.now(),
        )
    )

    assert len(scientist.completed_executions()) == 1


def test_successful_executions() -> None:
    scientist = AIScientist()

    scientist.start_execution(
        ResearchExecution(success=False)
    )

    scientist.start_execution(
        ResearchExecution(success=True)
    )

    assert len(scientist.successful_executions()) == 1


def test_total_executions() -> None:
    scientist = AIScientist()

    for _ in range(3):
        scientist.start_execution(ResearchExecution())

    assert scientist.total_executions() == 3


def test_record_execution() -> None:
    scientist = AIScientist()
    execution = ResearchExecution()

    result = scientist.record_execution(execution)

    assert result is execution
    assert scientist.total_executions() == 1
    assert scientist.executions[0] is execution


def test_record_execution_ignores_duplicate() -> None:
    scientist = AIScientist()
    execution = ResearchExecution()

    scientist.record_execution(execution)
    scientist.record_execution(execution)

    assert scientist.total_executions() == 1


def test_record_execution_accepts_distinct_executions() -> None:
    scientist = AIScientist()

    first = ResearchExecution()
    second = ResearchExecution()

    scientist.record_execution(first)
    scientist.record_execution(second)

    assert scientist.total_executions() == 2
    assert scientist.executions == [first, second]


def test_run_research_registers_and_completes_execution() -> None:
    scientist = AIScientist()

    question = SimpleNamespace(id="question-id")
    hypothesis = SimpleNamespace(id="hypothesis-id")

    experiment = Experiment(
        hypothesis_id=hypothesis.id,
    )

    result = SimpleNamespace(
        evidence=SimpleNamespace(id="evidence-id"),
        knowledge=SimpleNamespace(id="knowledge-id"),
    )

    engine = Mock()
    engine.run.return_value = result

    executor = Mock()

    execution = scientist.run_research(
        engine=engine,
        question=question,
        hypothesis=hypothesis,
        experiment=experiment,
        executor=executor,
    )

    assert scientist.total_executions() == 1
    assert scientist.executions[0] is execution

    assert execution.status == "COMPLETED"
    assert execution.success is True
    assert execution.is_completed()
    assert execution.result is result

    assert execution.question_id == question.id
    assert execution.hypothesis_id == hypothesis.id
    assert execution.experiment_id == experiment.id

    assert execution.evidence_id == "evidence-id"
    assert execution.knowledge_id == "knowledge-id"

    engine.run.assert_called_once_with(
        question=question,
        hypothesis=hypothesis,
        experiment=experiment,
        executor=executor,
    )


def test_run_research_records_failed_execution_and_reraises() -> None:
    scientist = AIScientist()

    question = SimpleNamespace(id="question-id")
    hypothesis = SimpleNamespace(id="hypothesis-id")

    experiment = Experiment(
        hypothesis_id=hypothesis.id,
    )

    engine = Mock()
    engine.run.side_effect = RuntimeError("engine failed")

    executor = Mock()

    with pytest.raises(
        RuntimeError,
        match="engine failed",
    ):
        scientist.run_research(
            engine=engine,
            question=question,
            hypothesis=hypothesis,
            experiment=experiment,
            executor=executor,
        )

    assert scientist.total_executions() == 1

    execution = scientist.executions[0]

    assert execution.status == "FAILED"
    assert execution.success is False
    assert execution.is_completed()
    assert execution.error == "engine failed"

    engine.run.assert_called_once_with(
        question=question,
        hypothesis=hypothesis,
        experiment=experiment,
        executor=executor,
    )


def test_run_research_registers_execution_only_once() -> None:
    scientist = AIScientist()

    question = SimpleNamespace(id="question-id")
    hypothesis = SimpleNamespace(id="hypothesis-id")

    experiment = Experiment(
        hypothesis_id=hypothesis.id,
    )

    result = SimpleNamespace(
        evidence=SimpleNamespace(id="evidence-id"),
        knowledge=SimpleNamespace(id="knowledge-id"),
    )

    engine = Mock()
    engine.run.return_value = result

    scientist.run_research(
        engine=engine,
        question=question,
        hypothesis=hypothesis,
        experiment=experiment,
        executor=Mock(),
    )

    assert scientist.total_executions() == 1


def test_run_research_rejects_experiment_for_another_hypothesis() -> None:
    scientist = AIScientist()

    question = SimpleNamespace(id="question-id")
    hypothesis = SimpleNamespace(id="hypothesis-id")

    experiment = Experiment(
        hypothesis_id="another-hypothesis-id",
    )

    engine = Mock()

    with pytest.raises(
        ValueError,
        match="experiment does not belong to hypothesis",
    ):
        scientist.run_research(
            engine=engine,
            question=question,
            hypothesis=hypothesis,
            experiment=experiment,
            executor=Mock(),
        )

    assert scientist.total_executions() == 0
    engine.run.assert_not_called()


def test_run_research_allows_empty_experiment_hypothesis_id() -> None:
    scientist = AIScientist()

    question = SimpleNamespace(id="question-id")
    hypothesis = SimpleNamespace(id="hypothesis-id")
    experiment = Experiment()

    result = SimpleNamespace(
        evidence=SimpleNamespace(id="evidence-id"),
        knowledge=SimpleNamespace(id="knowledge-id"),
    )

    engine = Mock()
    engine.run.return_value = result

    execution = scientist.run_research(
        engine=engine,
        question=question,
        hypothesis=hypothesis,
        experiment=experiment,
        executor=Mock(),
    )

    assert execution.status == "COMPLETED"
    assert execution.hypothesis_id == hypothesis.id
    assert scientist.total_executions() == 1

def test_run_campaign_completes_execution_for_each_experiment() -> None:
    scientist = AIScientist()
    engine = Mock()

    question = SimpleNamespace(id="question-1")
    hypothesis = SimpleNamespace(id="hypothesis-1")

    first_experiment = SimpleNamespace(
        id="experiment-1",
        hypothesis_id="hypothesis-1",
    )
    second_experiment = SimpleNamespace(
        id="experiment-2",
        hypothesis_id="hypothesis-1",
    )

    first_result = SimpleNamespace(
        evidence=SimpleNamespace(id="evidence-1"),
        knowledge=SimpleNamespace(id="knowledge-1"),
    )
    second_result = SimpleNamespace(
        evidence=SimpleNamespace(id="evidence-2"),
        knowledge=SimpleNamespace(id="knowledge-2"),
    )

    campaign = ResearchCampaign(
        hypothesis_id=hypothesis.id,
        experiment_ids=[
            first_experiment.id,
            second_experiment.id,
        ],
    )

    def run_campaign(**kwargs: object) -> list[object]:
        on_cycle_started = kwargs["on_cycle_started"]
        on_cycle_completed = kwargs["on_cycle_completed"]

        assert callable(on_cycle_started)
        assert callable(on_cycle_completed)

        on_cycle_started(first_experiment)
        on_cycle_completed(
            first_experiment,
            first_result,
        )

        on_cycle_started(second_experiment)
        on_cycle_completed(
            second_experiment,
            second_result,
        )

        return [
            first_result,
            second_result,
        ]

    engine.run_campaign.side_effect = run_campaign

    executions = scientist.run_campaign(
        engine=engine,
        question=question,
        hypothesis=hypothesis,
        campaign=campaign,
        experiments=[
            first_experiment,
            second_experiment,
        ],
        executor=Mock(),
    )

    assert executions == scientist.executions
    assert len(executions) == 2

    first_execution, second_execution = executions

    assert first_execution.experiment_id == first_experiment.id
    assert first_execution.status == "COMPLETED"
    assert first_execution.success is True
    assert first_execution.result is first_result
    assert first_execution.evidence_id == "evidence-1"
    assert first_execution.knowledge_id == "knowledge-1"

    assert second_execution.experiment_id == second_experiment.id
    assert second_execution.status == "COMPLETED"
    assert second_execution.success is True
    assert second_execution.result is second_result
    assert second_execution.evidence_id == "evidence-2"
    assert second_execution.knowledge_id == "knowledge-2"


def test_run_campaign_delegates_orchestration_to_engine() -> None:
    scientist = AIScientist()
    engine = Mock()

    question = SimpleNamespace(id="question-1")
    hypothesis = SimpleNamespace(id="hypothesis-1")
    experiment = SimpleNamespace(
        id="experiment-1",
        hypothesis_id="hypothesis-1",
    )

    campaign = ResearchCampaign(
        hypothesis_id=hypothesis.id,
        experiment_ids=[experiment.id],
    )

    executor = Mock()

    engine.run_campaign.return_value = []

    executions = scientist.run_campaign(
        engine=engine,
        question=question,
        hypothesis=hypothesis,
        campaign=campaign,
        experiments=[experiment],
        executor=executor,
    )

    assert executions == []

    engine.run_campaign.assert_called_once()

    call = engine.run_campaign.call_args

    assert call.kwargs["question"] is question
    assert call.kwargs["hypothesis"] is hypothesis
    assert call.kwargs["campaign"] is campaign
    assert call.kwargs["experiments"] == [experiment]
    assert call.kwargs["executor"] is executor
    assert callable(call.kwargs["on_cycle_started"])
    assert callable(call.kwargs["on_cycle_completed"])


def test_run_campaign_marks_current_execution_failed() -> None:
    scientist = AIScientist()
    engine = Mock()

    question = SimpleNamespace(id="question-1")
    hypothesis = SimpleNamespace(id="hypothesis-1")

    first_experiment = SimpleNamespace(
        id="experiment-1",
        hypothesis_id="hypothesis-1",
    )
    second_experiment = SimpleNamespace(
        id="experiment-2",
        hypothesis_id="hypothesis-1",
    )
    third_experiment = SimpleNamespace(
        id="experiment-3",
        hypothesis_id="hypothesis-1",
    )

    first_result = SimpleNamespace(
        evidence=SimpleNamespace(id="evidence-1"),
        knowledge=SimpleNamespace(id="knowledge-1"),
    )

    campaign = ResearchCampaign(
        hypothesis_id=hypothesis.id,
        experiment_ids=[
            first_experiment.id,
            second_experiment.id,
            third_experiment.id,
        ],
    )

    def run_campaign(**kwargs: object) -> list[object]:
        on_cycle_started = kwargs["on_cycle_started"]
        on_cycle_completed = kwargs["on_cycle_completed"]

        assert callable(on_cycle_started)
        assert callable(on_cycle_completed)

        on_cycle_started(first_experiment)
        on_cycle_completed(
            first_experiment,
            first_result,
        )

        on_cycle_started(second_experiment)

        raise RuntimeError("second cycle failed")

    engine.run_campaign.side_effect = run_campaign

    with pytest.raises(
        RuntimeError,
        match="second cycle failed",
    ):
        scientist.run_campaign(
            engine=engine,
            question=question,
            hypothesis=hypothesis,
            campaign=campaign,
            experiments=[
                first_experiment,
                second_experiment,
                third_experiment,
            ],
            executor=Mock(),
        )

    assert len(scientist.executions) == 2

    first_execution, second_execution = scientist.executions

    assert first_execution.experiment_id == first_experiment.id
    assert first_execution.status == "COMPLETED"
    assert first_execution.success is True
    assert first_execution.result is first_result

    assert second_execution.experiment_id == second_experiment.id
    assert second_execution.status == "FAILED"
    assert second_execution.success is False
    assert second_execution.result is None
    assert second_execution.error == "second cycle failed"

    assert all(
        execution.experiment_id != third_experiment.id
        for execution in scientist.executions
    )


def test_run_campaign_registers_each_execution_only_once() -> None:
    scientist = AIScientist()
    engine = Mock()

    question = SimpleNamespace(id="question-1")
    hypothesis = SimpleNamespace(id="hypothesis-1")
    experiment = SimpleNamespace(
        id="experiment-1",
        hypothesis_id="hypothesis-1",
    )

    result = SimpleNamespace(
        evidence=SimpleNamespace(id="evidence-1"),
        knowledge=SimpleNamespace(id="knowledge-1"),
    )

    campaign = ResearchCampaign(
        hypothesis_id=hypothesis.id,
        experiment_ids=[experiment.id],
    )

    def run_campaign(**kwargs: object) -> list[object]:
        on_cycle_started = kwargs["on_cycle_started"]
        on_cycle_completed = kwargs["on_cycle_completed"]

        assert callable(on_cycle_started)
        assert callable(on_cycle_completed)

        on_cycle_started(experiment)
        on_cycle_completed(
            experiment,
            result,
        )

        return [result]

    engine.run_campaign.side_effect = run_campaign

    executions = scientist.run_campaign(
        engine=engine,
        question=question,
        hypothesis=hypothesis,
        campaign=campaign,
        experiments=[experiment],
        executor=Mock(),
    )

    assert len(executions) == 1
    assert len(scientist.executions) == 1
    assert executions[0] is scientist.executions[0]
