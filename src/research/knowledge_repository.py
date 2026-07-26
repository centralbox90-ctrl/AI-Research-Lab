from typing import Protocol, runtime_checkable

from src.research.knowledge_item import KnowledgeItem


class KnowledgeItemConflictError(ValueError):
    """
    Raised when an item ID is already bound to other content.
    """

    def __init__(
        self,
        *,
        item_id: str,
        existing_fingerprint: str,
        incoming_fingerprint: str,
    ) -> None:
        self.item_id = item_id
        self.existing_fingerprint = (
            existing_fingerprint
        )
        self.incoming_fingerprint = (
            incoming_fingerprint
        )

        super().__init__(
            f"knowledge item {item_id!r} already "
            "exists with different content"
        )


@runtime_checkable
class KnowledgeRepository(Protocol):
    """
    Persistence boundary for admitted KnowledgeItem objects.
    """

    def save(
        self,
        item: KnowledgeItem,
    ) -> None:
        """Persist an admitted item without silent overwrite."""

    def get(
        self,
        item_id: str,
    ) -> KnowledgeItem | None:
        """Return an item by ID or None when it is unknown."""

    def list_all(
        self,
    ) -> tuple[KnowledgeItem, ...]:
        """Return all items in deterministic ID order."""
