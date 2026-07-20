from datetime import datetime, timedelta

from src.research.research_execution import ResearchExecution


def test_research_execution_defaults() -> None:
    execution = ResearchExecution()

    assert execution.question_id == ""
    assert execution.hypothesis_id == ""
    assert execution.experiment_id == ""
    assert execution.specification_id == ""
    assert execution.evidence_id == ""
    assert execution.finding_id == ""
    assert execution.knowledge_id == ""
    assert execution.status == "NEW"
    assert execution.success is False
    assert execution.completed_at is None
    assert execution.notes == ""


def test_research_execution_construction() -> None:
    started_at = datetime(2026, 7, 19, 10, 0, 0)
    completed_at = datetime(2026, 7, 19, 10, 5, 0)

    execution = ResearchExecution(
        question_id="q-1",
        hypothesis_id="h-1",
        experiment_id="exp-1",
        specification_id="spec-1",
        evidence_id="ev-1",
        finding_id="f-1",
        knowledge_id="k-1",
        started_at=started_at,
        completed_at=completed_at,
        status="COMPLETED",
        success=True,
        notes="done",
    )

    assert execution.question_id == "q-1"
    assert execution.hypothesis_id == "h-1"
    assert execution.experiment_id == "exp-1"
    assert execution.specification_id == "spec-1"
    assert execution.evidence_id == "ev-1"
    assert execution.finding_id == "f-1"
    assert execution.knowledge_id == "k-1"
    assert execution.status == "COMPLETED"
    assert execution.success is True
    assert execution.notes == "done"


def test_research_execution_is_mutable() -> None:
    execution = ResearchExecution()

    execution.status = "RUNNING"
    execution.success = True
    execution.notes = "updated"

    assert execution.status == "RUNNING"
    assert execution.success is True
    assert execution.notes == "updated"


def test_is_completed_returns_false_without_completed_at() -> None:
    execution = ResearchExecution()

    assert execution.is_completed() is False


def test_is_completed_returns_true_with_completed_at() -> None:
    execution = ResearchExecution(
        completed_at=datetime.now(),
    )

    assert execution.is_completed() is True


def test_duration_returns_elapsed_seconds() -> None:
    started_at = datetime(2026, 7, 19, 10, 0, 0)
    completed_at = started_at + timedelta(seconds=90)

    execution = ResearchExecution(
        started_at=started_at,
        completed_at=completed_at,
    )

    assert execution.duration() == 90.0
def test_complete_execution() -> None:
    execution = ResearchExecution()
    result = object()

    execution.complete(result)

    assert execution.status == "COMPLETED"
    assert execution.success is True
    assert execution.completed_at is not None
    assert execution.result is result
    assert execution.error == ""


def test_fail_execution() -> None:
    execution = ResearchExecution()

    execution.fail(RuntimeError("engine failed"))

    assert execution.status == "FAILED"
    assert execution.success is False
    assert execution.completed_at is not None
    assert execution.error == "engine failed"