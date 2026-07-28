from __future__ import annotations

import json

from src.application.generate_research_questions_from_knowledge_repositories import (
    GenerateResearchQuestionsFromKnowledgeRepositories,
)
from src.application.knowledge_research_questions_artifact_envelope_factory import (
    KnowledgeResearchQuestionsArtifactEnvelopeFactory,
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
        artifact_envelope_factory: (
            KnowledgeResearchQuestionsArtifactEnvelopeFactory
            | None
        ) = None,
    ) -> None:
        if not isinstance(
            application,
            GenerateResearchQuestionsFromKnowledgeRepositories,
        ):
            raise TypeError(
                "application must be a "
                "GenerateResearchQuestionsFromKnowledgeRepositories"
            )

        if (
            artifact_envelope_factory is not None
            and not isinstance(
                artifact_envelope_factory,
                KnowledgeResearchQuestionsArtifactEnvelopeFactory,
            )
        ):
            raise TypeError(
                "artifact_envelope_factory must be a "
                "KnowledgeResearchQuestionsArtifactEnvelopeFactory "
                "or None"
            )

        self._application = application
        self._artifact_envelope_factory = (
            artifact_envelope_factory
        )

    def execute(
        self,
        *,
        indent: int | None = 2,
        correlation_id: str | None = None,
    ) -> str:
        result = self._application.execute()

        if self._artifact_envelope_factory is not None:
            payload = (
                self._artifact_envelope_factory.create(
                    result=result,
                    correlation_id=correlation_id,
                ).to_dict()
            )
        else:
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
