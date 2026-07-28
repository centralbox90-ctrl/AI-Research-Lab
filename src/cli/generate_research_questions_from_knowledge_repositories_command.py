from __future__ import annotations

import json

from src.application.build_knowledge_graph_snapshot import (
    BuildKnowledgeGraphSnapshot,
)
from src.application.generate_research_questions_from_knowledge_snapshot import (
    GenerateResearchQuestionsFromKnowledgeSnapshot,
)
from src.cli.research_questions_presenter import (
    present_research_questions,
)


class GenerateResearchQuestionsFromKnowledgeRepositoriesCommand:
    """
    Builds a stored Knowledge snapshot and renders questions.
    """

    def __init__(
        self,
        *,
        snapshot_builder: BuildKnowledgeGraphSnapshot,
        application: (
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
            application,
            GenerateResearchQuestionsFromKnowledgeSnapshot,
        ):
            raise TypeError(
                "application must be a "
                "GenerateResearchQuestionsFromKnowledgeSnapshot"
            )

        self._snapshot_builder = (
            snapshot_builder
        )
        self._application = application

    def execute(
        self,
        *,
        indent: int | None = 2,
    ) -> str:
        snapshot = (
            self._snapshot_builder.execute()
        )
        questions = self._application.execute(
            snapshot
        )
        payload = present_research_questions(
            snapshot=snapshot,
            questions=questions,
        )

        return json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            indent=indent,
        )
