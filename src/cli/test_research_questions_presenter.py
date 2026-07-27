from datetime import datetime, timezone

import pytest

from src.cli.research_questions_presenter import (
    present_research_questions,
)
from src.research.knowledge_graph_snapshot import (
    KnowledgeGraphSnapshot,
)
from src.research.question import ResearchQuestion


def build_snapshot() -> KnowledgeGraphSnapshot:
    return KnowledgeGraphSnapshot(
        items=(),
        relations=(),
    )


def build_question(
    *,
    question_id: str = "question-a",
) -> ResearchQuestion:
    return ResearchQuestion(
        id=question_id,
        statement="What evidence is missing?",
        description="Investigate the knowledge gap.",
        created_at=datetime(
            2026,
            1,
            1,
            tzinfo=timezone.utc,
        ),
    )


def test_presents_versioned_json_compatible_artifact(
) -> None:
    snapshot = build_snapshot()
    question = build_question()

    payload = present_research_questions(
        snapshot=snapshot,
        questions=(question,),
    )

    assert payload == {
        "artifact_type": (
            "knowledge_research_questions"
        ),
        "artifact_version": 1,
        "snapshot_fingerprint": (
            snapshot.fingerprint
        ),
        "question_count": 1,
        "questions": [
            {
                "id": "question-a",
                "statement": (
                    "What evidence is missing?"
                ),
                "description": (
                    "Investigate the knowledge gap."
                ),
                "created_at": (
                    "2026-01-01T00:00:00+00:00"
                ),
                "status": "NEW",
            }
        ],
    }


def test_preserves_question_order() -> None:
    payload = present_research_questions(
        snapshot=build_snapshot(),
        questions=(
            build_question(
                question_id="question-b",
            ),
            build_question(
                question_id="question-a",
            ),
        ),
    )

    assert [
        question["id"]
        for question in payload["questions"]
    ] == [
        "question-b",
        "question-a",
    ]


def test_rejects_invalid_snapshot() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "snapshot must be a "
            "KnowledgeGraphSnapshot"
        ),
    ):
        present_research_questions(
            snapshot=object(),
            questions=(),
        )


def test_rejects_non_tuple_questions() -> None:
    with pytest.raises(
        TypeError,
        match="questions must be a tuple",
    ):
        present_research_questions(
            snapshot=build_snapshot(),
            questions=[],
        )


def test_rejects_invalid_question() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "each question must be a "
            "ResearchQuestion"
        ),
    ):
        present_research_questions(
            snapshot=build_snapshot(),
            questions=(object(),),
        )


def test_rejects_duplicate_question_ids() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "questions must have unique IDs"
        ),
    ):
        present_research_questions(
            snapshot=build_snapshot(),
            questions=(
                build_question(),
                build_question(),
            ),
        )
