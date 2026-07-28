from __future__ import annotations

import json

from src.application.generate_research_questions_from_knowledge_repositories import (
    GenerateResearchQuestionsFromKnowledgeRepositories,
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
        application: (
            GenerateResearchQuestionsFromKnowledgeRepositories
        ),
    ) -> None:
        if not isinstance(
            application,
            GenerateResearchQuestionsFromKnowledgeRepositories,
        ):
            raise TypeError(
                "application must be a "
                "GenerateResearchQuestionsFromKnowledgeRepositories"
            )

        self._application = application

    def execute(
        self,
        *,
        indent: int | None = 2,
    ) -> str:
        result = self._application.execute()
        payload = present_research_questions(
            snapshot=result.snapshot,
            questions=result.questions,
        )

        return json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            indent=indent,
        )
