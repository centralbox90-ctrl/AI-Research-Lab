from __future__ import annotations

from dataclasses import dataclass

from src.application.build_knowledge_graph_snapshot import (
    BuildKnowledgeGraphSnapshot,
)
from src.application.generate_research_questions_from_knowledge_snapshot import (
    GenerateResearchQuestionsFromKnowledgeSnapshot,
)
from src.research.knowledge_graph_snapshot import (
    KnowledgeGraphSnapshot,
)
from src.research.question import ResearchQuestion


@dataclass(frozen=True, slots=True)
class KnowledgeResearchQuestionsResult:
    """
    Application result for repository-backed question generation.
    """

    snapshot: KnowledgeGraphSnapshot
    questions: tuple[ResearchQuestion, ...]

    def __post_init__(self) -> None:
        if not isinstance(
            self.snapshot,
            KnowledgeGraphSnapshot,
        ):
            raise TypeError(
                "snapshot must be a "
                "KnowledgeGraphSnapshot"
            )

        if not isinstance(self.questions, tuple):
            raise TypeError(
                "questions must be a tuple"
            )

        if any(
            not isinstance(
                question,
                ResearchQuestion,
            )
            for question in self.questions
        ):
            raise TypeError(
                "questions must contain only "
                "ResearchQuestion values"
            )

        question_ids = tuple(
            question.id
            for question in self.questions
        )

        if len(question_ids) != len(
            set(question_ids)
        ):
            raise ValueError(
                "questions must have unique IDs"
            )


class GenerateResearchQuestionsFromKnowledgeRepositories:
    """
    Generates questions from persistent Knowledge repositories.
    """

    def __init__(
        self,
        *,
        snapshot_builder: BuildKnowledgeGraphSnapshot,
        question_generator: (
            GenerateResearchQuestionsFromKnowledgeSnapshot
        ),
    ) -> None:
        if not isinstance(
            snapshot_builder,
            BuildKnowledgeGraphSnapshot,
        ):
            raise TypeError(
                "snapshot_builder must be a "
                "BuildKnowledgeGraphSnapshot"
            )

        if not isinstance(
            question_generator,
            GenerateResearchQuestionsFromKnowledgeSnapshot,
        ):
            raise TypeError(
                "question_generator must be a "
                "GenerateResearchQuestionsFromKnowledgeSnapshot"
            )

        self._snapshot_builder = snapshot_builder
        self._question_generator = (
            question_generator
        )

    def execute(
        self,
    ) -> KnowledgeResearchQuestionsResult:
        snapshot = self._snapshot_builder.execute()
        questions = self._question_generator.execute(
            snapshot
        )

        return KnowledgeResearchQuestionsResult(
            snapshot=snapshot,
            questions=questions,
        )
