from __future__ import annotations

from src.research.knowledge_graph_snapshot import (
    KnowledgeGraphSnapshot,
)
from src.research.knowledge_item import (
    KnowledgeItem,
)
from src.research.knowledge_relation_repository import (
    KnowledgeRelationRepository,
)
from src.research.knowledge_repository import (
    KnowledgeRepository,
)


class BuildKnowledgeGraphSnapshot:
    """
    Builds a complete snapshot from persistent Knowledge ports.
    """

    def __init__(
        self,
        *,
        knowledge_repository: KnowledgeRepository,
        relation_repository: (
            KnowledgeRelationRepository
        ),
    ) -> None:
        if not isinstance(
            knowledge_repository,
            KnowledgeRepository,
        ):
            raise TypeError(
                "knowledge_repository must implement "
                "KnowledgeRepository"
            )

        if not isinstance(
            relation_repository,
            KnowledgeRelationRepository,
        ):
            raise TypeError(
                "relation_repository must implement "
                "KnowledgeRelationRepository"
            )

        self._knowledge_repository = (
            knowledge_repository
        )
        self._relation_repository = (
            relation_repository
        )

    def execute(
        self,
    ) -> KnowledgeGraphSnapshot:
        latest_items = (
            self._knowledge_repository.list_all()
        )
        relations = (
            self._relation_repository.list_all()
        )
        items_by_fingerprint: dict[
            str,
            KnowledgeItem,
        ] = {
            item.fingerprint: item
            for item in latest_items
        }

        for relation in relations:
            items_by_fingerprint.setdefault(
                relation.source.fingerprint,
                relation.source,
            )
            items_by_fingerprint.setdefault(
                relation.target.fingerprint,
                relation.target,
            )

        return KnowledgeGraphSnapshot(
            items=tuple(
                items_by_fingerprint.values()
            ),
            relations=relations,
        )
