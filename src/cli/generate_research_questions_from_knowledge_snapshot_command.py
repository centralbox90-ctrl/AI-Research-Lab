from __future__ import annotations

import json
from pathlib import Path

from src.application.generate_research_questions_from_knowledge_snapshot import (
    GenerateResearchQuestionsFromKnowledgeSnapshot,
)
from src.application.knowledge_graph_snapshot_loader import (
    KnowledgeGraphSnapshotLoader,
)
from src.cli.research_questions_presenter import (
    present_research_questions,
)


class GenerateResearchQuestionsFromKnowledgeSnapshotCommand:
    """
    Loads a knowledge snapshot and renders generated questions.
    """

    def __init__(
        self,
        *,
        application: (
            GenerateResearchQuestionsFromKnowledgeSnapshot
        ),
        snapshot_loader: (
            KnowledgeGraphSnapshotLoader | None
        ) = None,
    ) -> None:
        if not isinstance(
            application,
            GenerateResearchQuestionsFromKnowledgeSnapshot,
        ):
            raise TypeError(
                "application must be a "
                "GenerateResearchQuestionsFromKnowledgeSnapshot"
            )

        if (
            snapshot_loader is not None
            and not isinstance(
                snapshot_loader,
                KnowledgeGraphSnapshotLoader,
            )
        ):
            raise TypeError(
                "snapshot_loader must be a "
                "KnowledgeGraphSnapshotLoader or None"
            )

        self._application = application
        self._snapshot_loader = (
            snapshot_loader
            or KnowledgeGraphSnapshotLoader()
        )

    def execute(
        self,
        snapshot_path: str | Path,
        *,
        indent: int | None = 2,
    ) -> str:
        snapshot = self._snapshot_loader.load(
            snapshot_path
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
