from src.research.knowledge_contradiction import (
    KnowledgeContradiction,
)
from src.research.knowledge_relation import (
    KnowledgeRelation,
    KnowledgeRelationType,
)
from src.research.knowledge_relation_repository import (
    KnowledgeRelationRepository,
)
from src.research.knowledge_repository import (
    KnowledgeRepository,
)
from src.research.knowledge_revision import (
    KnowledgeRevision,
)


class KnowledgeGraphRelationRegistrar:
    """
    Projects stored knowledge evolution into typed graph relations.
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

    def register_contradiction(
        self,
        contradiction: KnowledgeContradiction,
    ) -> KnowledgeRelation:
        if not isinstance(
            contradiction,
            KnowledgeContradiction,
        ):
            raise TypeError(
                "contradiction must be a "
                "KnowledgeContradiction"
            )

        if not any(
            stored.fingerprint
            == contradiction.fingerprint
            for stored
            in (
                self._knowledge_repository
                .list_contradictions()
            )
        ):
            raise ValueError(
                "contradiction must be registered "
                "before graph projection"
            )

        source, target = contradiction.items
        relation = KnowledgeRelation(
            source=source,
            target=target,
            relation_type=(
                KnowledgeRelationType.CONTRADICTS
            ),
            reason=contradiction.reason,
        )
        self._relation_repository.save(
            relation
        )

        return relation

    def register_revision(
        self,
        revision: KnowledgeRevision,
    ) -> KnowledgeRelation | None:
        if not isinstance(
            revision,
            KnowledgeRevision,
        ):
            raise TypeError(
                "revision must be a "
                "KnowledgeRevision"
            )

        stored_revision = (
            self._knowledge_repository.get_version(
                revision.item.id,
                revision.item.version,
            )
        )

        if (
            stored_revision is None
            or stored_revision.fingerprint
            != revision.fingerprint
        ):
            raise ValueError(
                "revision must be stored before "
                "graph projection"
            )

        if revision.supersedes_version is None:
            return None

        previous_revision = (
            self._knowledge_repository.get_version(
                revision.item.id,
                revision.supersedes_version,
            )
        )

        if previous_revision is None:
            raise ValueError(
                "superseded revision must be stored "
                "before graph projection"
            )

        relation = KnowledgeRelation(
            source=revision.item,
            target=previous_revision.item,
            relation_type=(
                KnowledgeRelationType.SUPERSEDES
            ),
            reason=revision.change_reason,
        )
        self._relation_repository.save(
            relation
        )

        return relation
