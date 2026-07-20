from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

import pytest

from src.research.question import ResearchQuestion
from src.research.research_types import ResearchStatus


def test_research_question_is_created():
    created_at = datetime(
        2026,
        7,
        19,
        12,
        0,
        tzinfo=timezone.utc,
    )

    question = ResearchQuestion(
        id="question-1",
        statement=(
            "How does price behave after Williams %R "
            "exits the oversold region?"
        ),
        description="Williams %R oversold exit study.",
        created_at=created_at,
        status=ResearchStatus.PLANNED,
    )

    assert question.id == "question-1"
    assert (
        question.statement
        == (
            "How does price behave after Williams %R "
            "exits the oversold region?"
        )
    )
    assert (
        question.description
        == "Williams %R oversold exit study."
    )
    assert question.created_at == created_at
    assert question.status is ResearchStatus.PLANNED


def test_research_question_is_immutable():
    question = ResearchQuestion(
        statement="How does the market respond?"
    )

    with pytest.raises(FrozenInstanceError):
        question.statement = "Changed statement"


def test_research_question_is_serializable():
    created_at = datetime(
        2026,
        7,
        19,
        12,
        0,
        tzinfo=timezone.utc,
    )

    question = ResearchQuestion(
        id="question-1",
        statement="How does the market respond?",
        description="Research description.",
        created_at=created_at,
        status=ResearchStatus.NEW,
    )

    assert question.to_dict() == {
        "id": "question-1",
        "statement": "How does the market respond?",
        "description": "Research description.",
        "created_at": "2026-07-19T12:00:00+00:00",
        "status": "NEW",
    }


def test_research_question_rejects_empty_statement():
    with pytest.raises(
        ValueError,
        match="statement must not be empty",
    ):
        ResearchQuestion(statement="   ")


def test_research_question_rejects_invalid_status():
    with pytest.raises(
        TypeError,
        match="status must be a ResearchStatus",
    ):
        ResearchQuestion(
            statement="How does the market respond?",
            status="NEW",
        )
