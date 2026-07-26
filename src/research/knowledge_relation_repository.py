from typing import Protocol, runtime_checkable

from src.research.knowledge_relation import (
    KnowledgeRelation,
    KnowledgeRelationType,
)


class KnowledgeRelationReferenceError(
    ValueError
):
    """
    Raised when a relation endpoint is not an exact stored item version.
    """

    def __init__(
        self,
        *,
        endpoint: str,
        item_id: str,
        version: int,
    ) -> None:
        self.endpoint = endpoint
        self.item_id = item_id
        self.version = version

        super().__init__(
            f"{endpoint} knowledge item "
            f"{item_id!r} version {version} "
            "is not stored with matching content"
        )


@runtime_checkable
class KnowledgeRelationRepository(
    Protocol
):
    """
    Persistence boundary for append-only KnowledgeRelation objects.
    """

    def save(
        self,
        relation: KnowledgeRelation,
    ) -> None:
        """Append a relation without replacing prior records."""

    def list_all(
        self,
    ) -> tuple[KnowledgeRelation, ...]:
        """Return all relations in deterministic order."""

    def outgoing(
        self,
        item_id: str,
        *,
        version: int | None = None,
        relation_type: (
            KnowledgeRelationType | None
        ) = None,
    ) -> tuple[KnowledgeRelation, ...]:
        """Return deterministic relations originating at an item."""

    def incoming(
        self,
        item_id: str,
        *,
        version: int | None = None,
        relation_type: (
            KnowledgeRelationType | None
        ) = None,
    ) -> tuple[KnowledgeRelation, ...]:
        """Return deterministic relations targeting an item."""

    def relations_for(
        self,
        item_id: str,
        *,
        version: int | None = None,
        relation_type: (
            KnowledgeRelationType | None
        ) = None,
    ) -> tuple[KnowledgeRelation, ...]:
        """Return deterministic incident relations for an item."""
