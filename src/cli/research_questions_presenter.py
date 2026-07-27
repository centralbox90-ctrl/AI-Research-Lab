from __future__ import annotations

from src.research.knowledge_graph_snapshot import (
    KnowledgeGraphSnapshot,
)
from src.research.question import ResearchQuestion


def present_research_questions(
    *,
    snapshot: KnowledgeGraphSnapshot,
    questions: tuple[ResearchQuestion, ...],
) -> dict[str, object]:
    """
    Build a versioned JSON-compatible research-question artifact.
    """

    if not isinstance(
        snapshot,
        KnowledgeGraphSnapshot,
    ):
        raise TypeError(
            "snapshot must be a "
            "KnowledgeGraphSnapshot"
        )

    if not isinstance(questions, tuple):
        raise TypeError(
            "questions must be a tuple"
        )

    for question in questions:
        if not isinstance(
            question,
            ResearchQuestion,
        ):
            raise TypeError(
                "each question must be a "
                "ResearchQuestion"
            )

    question_ids = tuple(
        question.id
        for question in questions
    )

    if len(question_ids) != len(set(question_ids)):
        raise ValueError(
            "questions must have unique IDs"
        )

    return {
        "artifact_type": (
            "knowledge_research_questions"
        ),
        "artifact_version": 1,
        "snapshot_fingerprint": (
            snapshot.fingerprint
        ),
        "question_count": len(questions),
        "questions": [
            question.to_dict()
            for question in questions
        ],
    }
