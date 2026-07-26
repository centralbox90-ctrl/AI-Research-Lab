from src.research.knowledge_item import KnowledgeItem
from src.research.knowledge_repository import (
    KnowledgeItemConflictError,
)


class InMemoryKnowledgeRepository:
    """
    Append-only in-memory storage for admitted KnowledgeItem objects.
    """

    def __init__(self) -> None:
        self._items: dict[str, KnowledgeItem] = {}

    def save(
        self,
        item: KnowledgeItem,
    ) -> None:
        if not isinstance(item, KnowledgeItem):
            raise TypeError(
                "item must be a KnowledgeItem"
            )

        existing = self._items.get(item.id)

        if existing is None:
            self._items[item.id] = item
            return

        if existing != item:
            raise KnowledgeItemConflictError(
                item_id=item.id,
                existing_fingerprint=(
                    existing.fingerprint
                ),
                incoming_fingerprint=(
                    item.fingerprint
                ),
            )

    def get(
        self,
        item_id: str,
    ) -> KnowledgeItem | None:
        normalized_id = self._normalize_item_id(
            item_id
        )

        return self._items.get(normalized_id)

    def list_all(
        self,
    ) -> tuple[KnowledgeItem, ...]:
        return tuple(
            self._items[item_id]
            for item_id in sorted(self._items)
        )

    @staticmethod
    def _normalize_item_id(
        value: object,
    ) -> str:
        if not isinstance(value, str):
            raise TypeError(
                "item_id must be a string"
            )

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                "item_id must not be empty"
            )

        return normalized
