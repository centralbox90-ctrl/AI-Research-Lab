from datetime import datetime

from src.research.knowledge import Knowledge


def test_knowledge_creates_with_defaults() -> None:
    knowledge = Knowledge()

    assert knowledge.id
    assert knowledge.question_id == ""
    assert knowledge.hypothesis_id == ""
    assert knowledge.experiment_id == ""
    assert knowledge.title == ""
    assert knowledge.statement == ""
    assert knowledge.confidence == 0.0
    assert knowledge.is_provisional is True
    assert knowledge.basis == ""
    assert isinstance(knowledge.created_at, datetime)
    assert knowledge.tags == []
    assert knowledge.notes == ""


def test_knowledge_accepts_research_context() -> None:
    knowledge = Knowledge(
        id="knowledge-001",
        question_id="question-001",
        hypothesis_id="hypothesis-001",
        experiment_id="experiment-001",
        title="Williams oversold response",
        statement="Returns improve after oversold observations.",
        confidence=0.75,
        is_provisional=True,
        basis="Three completed experiments.",
        tags=["williams-r", "mean-return"],
        notes="Requires broader validation.",
    )

    assert knowledge.id == "knowledge-001"
    assert knowledge.question_id == "question-001"
    assert knowledge.hypothesis_id == "hypothesis-001"
    assert knowledge.experiment_id == "experiment-001"
    assert knowledge.title == "Williams oversold response"
    assert knowledge.confidence == 0.75
    assert knowledge.tags == [
        "williams-r",
        "mean-return",
    ]


def test_knowledge_tags_are_not_shared() -> None:
    first = Knowledge()
    second = Knowledge()

    first.tags.append("first")

    assert first.tags == ["first"]
    assert second.tags == []


def test_knowledge_is_mutable() -> None:
    knowledge = Knowledge(
        confidence=0.25,
        is_provisional=True,
    )

    knowledge.confidence = 0.80
    knowledge.is_provisional = False

    assert knowledge.confidence == 0.80
    assert knowledge.is_provisional is False


def test_knowledge_summary_contains_research_context() -> None:
    knowledge = Knowledge(
        id="knowledge-001",
        question_id="question-001",
        hypothesis_id="hypothesis-001",
        experiment_id="experiment-001",
        title="Williams investigation",
        statement="The observed effect is positive.",
        confidence=0.75,
        is_provisional=True,
        basis="Experiment evidence",
    )

    summary = knowledge.summary()

    assert "Knowledge: Williams investigation" in summary
    assert "ID: knowledge-001" in summary
    assert "Question: question-001" in summary
    assert "Hypothesis: hypothesis-001" in summary
    assert "Experiment: experiment-001" in summary
    assert "Confidence: 0.75" in summary
    assert "Provisional: True" in summary
    assert "Basis: Experiment evidence" in summary
    assert "Statement: The observed effect is positive." in summary


def test_knowledge_summary_uses_none_for_empty_optional_text() -> None:
    knowledge = Knowledge(
        title="Empty evidence",
    )

    summary = knowledge.summary()

    assert "Basis: None" in summary
    assert "Statement: None" in summary