from typing import Protocol, runtime_checkable

from src.research.knowledge_item import KnowledgeItem
from src.research.knowledge_revision import (
    KnowledgeRevision,
)


class KnowledgeItemConflictError(ValueError):
    """
    Raised when an item version is bound to other content.
    """

    def __init__(
        self,
        *,
        item_id: str,
        version: int,
        existing_fingerprint: str,
        incoming_fingerprint: str,
    ) -> None:
        self.item_id = item_id
        self.version = version
        self.existing_fingerprint = (
            existing_fingerprint
        )
        self.incoming_fingerprint = (
            incoming_fingerprint
        )

        super().__init__(
            f"knowledge item {item_id!r} version "
            f"{version} already exists with "
            "different content"
        )


class KnowledgeRevisionSequenceError(
    ValueError
):
    """
    Raised when a revision is not the next stored version.
    """

    def __init__(
        self,
        *,
        item_id: str,
        expected_version: int,
        incoming_version: int,
    ) -> None:
        self.item_id = item_id
        self.expected_version = expected_version
        self.incoming_version = incoming_version

        super().__init__(
            f"knowledge item {item_id!r} expected "
            f"version {expected_version}, received "
            f"version {incoming_version}"
        )


@runtime_checkable
class KnowledgeRepository(Protocol):
    """
    Persistence boundary for versioned KnowledgeRevision objects.
    """

    def save(
        self,
        revision: KnowledgeRevision,
    ) -> None:
        """Append a revision without deleting history."""

    def get(
        self,
        item_id: str,
    ) -> KnowledgeItem | None:
        """Return the latest item or None when unknown."""

    def get_version(
        self,
        item_id: str,
        version: int,
    ) -> KnowledgeRevision | None:
        """Return one stored revision by item ID and version."""

    def history(
        self,
        item_id: str,
    ) -> tuple[KnowledgeRevision, ...]:
        """Return revisions in ascending version order."""

    def list_all(
        self,
    ) -> tuple[KnowledgeItem, ...]:
        """Return latest items in deterministic ID order."""
