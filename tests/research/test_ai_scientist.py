from datetime import datetime
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from src.research.ai_scientist import AIScientist
from src.research.experiment import Experiment
from src.research.research_execution import ResearchExecution


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
