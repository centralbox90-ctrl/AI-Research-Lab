from enum import Enum

from src.research.knowledge_item import KnowledgeItem
from src.research.knowledge_relation import (
    KnowledgeRelation,
    KnowledgeRelationType,
)
from src.research.knowledge_relation_repository import (
    KnowledgeRelationRepository,
)


class KnowledgeTraversalDirection(
    str,
    Enum,
):
    """Supported directions for graph navigation."""

    OUTGOING = "outgoing"
    INCOMING = "incoming"
    BOTH = "both"


def _normalize_item(
    value: object,
) -> KnowledgeItem:
    if not isinstance(value, KnowledgeItem):
        raise TypeError(
            "item must be a KnowledgeItem"
        )

    return value


def _normalize_direction(
    value: object,
) -> KnowledgeTraversalDirection:
    if not isinstance(
        value,
        KnowledgeTraversalDirection,
    ):
        raise TypeError(
            "direction must be a "
            "KnowledgeTraversalDirection"
        )

    return value


def _normalize_relation_types(
    value: object,
) -> tuple[KnowledgeRelationType, ...] | None:
    if value is None:
        return None

    if not isinstance(value, tuple):
        raise TypeError(
            "relation_types must be a tuple "
            "or None"
        )

    normalized: list[
        KnowledgeRelationType
    ] = []

    for relation_type in value:
        if not isinstance(
            relation_type,
            KnowledgeRelationType,
        ):
            raise TypeError(
                "each relation type must be a "
                "KnowledgeRelationType"
            )

        normalized.append(relation_type)

    if len(normalized) != len(set(normalized)):
        raise ValueError(
            "relation_types must not contain "
            "duplicates"
        )

    return tuple(
        sorted(
            normalized,
            key=lambda relation_type: (
                relation_type.value
            ),
        )
    )


def _normalize_max_depth(
    value: object,
) -> int:
    if (
        not isinstance(value, int)
        or isinstance(value, bool)
    ):
        raise TypeError(
            "max_depth must be an integer"
        )

    if value < 0:
        raise ValueError(
            "max_depth must not be negative"
        )

    return value


def _item_key(
    item: KnowledgeItem,
) -> tuple[str, int, str]:
    return (
        item.id,
        item.version,
        item.fingerprint,
    )


class KnowledgeGraph:
    """
    Deterministic read model over stored knowledge relations.
    """

    def __init__(
        self,
        repository: KnowledgeRelationRepository,
    ) -> None:
        if not isinstance(
            repository,
            KnowledgeRelationRepository,
        ):
            raise TypeError(
                "repository must implement "
                "KnowledgeRelationRepository"
            )

        self._repository = repository

    def relations(
        self,
    ) -> tuple[KnowledgeRelation, ...]:
        """Return every stored relation in repository order."""

        return self._repository.list_all()

    def neighbors(
        self,
        item: KnowledgeItem,
        *,
        direction: KnowledgeTraversalDirection = (
            KnowledgeTraversalDirection.BOTH
        ),
        relation_types: (
            tuple[KnowledgeRelationType, ...]
            | None
        ) = None,
    ) -> tuple[KnowledgeItem, ...]:
        normalized_item = _normalize_item(item)
        normalized_direction = (
            _normalize_direction(direction)
        )
        normalized_relation_types = (
            _normalize_relation_types(
                relation_types
            )
        )

        return self._neighbors(
            normalized_item,
            direction=normalized_direction,
            relation_types=(
                normalized_relation_types
            ),
        )

    def traverse(
        self,
        start: KnowledgeItem,
        *,
        max_depth: int,
        direction: KnowledgeTraversalDirection = (
            KnowledgeTraversalDirection.OUTGOING
        ),
        relation_types: (
            tuple[KnowledgeRelationType, ...]
            | None
        ) = None,
    ) -> tuple[KnowledgeItem, ...]:
        normalized_start = _normalize_item(start)
        normalized_max_depth = (
            _normalize_max_depth(max_depth)
        )
        normalized_direction = (
            _normalize_direction(direction)
        )
        normalized_relation_types = (
            _normalize_relation_types(
                relation_types
            )
        )

        if normalized_max_depth == 0:
            return ()

        visited = {
            normalized_start.fingerprint
        }
        frontier = (
            normalized_start,
        )
        result: list[KnowledgeItem] = []

        for _ in range(normalized_max_depth):
            next_items: dict[
                str,
                KnowledgeItem,
            ] = {}

            for item in frontier:
                for neighbor in self._neighbors(
                    item,
                    direction=normalized_direction,
                    relation_types=(
                        normalized_relation_types
                    ),
                ):
                    if (
                        neighbor.fingerprint
                        in visited
                    ):
                        continue

                    next_items.setdefault(
                        neighbor.fingerprint,
                        neighbor,
                    )

            if not next_items:
                break

            frontier = tuple(
                sorted(
                    next_items.values(),
                    key=_item_key,
                )
            )
            visited.update(next_items)
            result.extend(frontier)

        return tuple(result)

    def _neighbors(
        self,
        item: KnowledgeItem,
        *,
        direction: KnowledgeTraversalDirection,
        relation_types: (
            tuple[KnowledgeRelationType, ...]
            | None
        ),
    ) -> tuple[KnowledgeItem, ...]:
        if (
            direction
            is KnowledgeTraversalDirection.OUTGOING
        ):
            relations = self._repository.outgoing(
                item.id,
                version=item.version,
            )
        elif (
            direction
            is KnowledgeTraversalDirection.INCOMING
        ):
            relations = self._repository.incoming(
                item.id,
                version=item.version,
            )
        else:
            relations = (
                self._repository.relations_for(
                    item.id,
                    version=item.version,
                )
            )

        neighbors: dict[
            str,
            KnowledgeItem,
        ] = {}

        for relation in relations:
            if (
                relation_types is not None
                and relation.relation_type
                not in relation_types
            ):
                continue

            neighbor: KnowledgeItem | None = None

            if (
                direction
                is not KnowledgeTraversalDirection.INCOMING
                and relation.source == item
            ):
                neighbor = relation.target
            elif (
                direction
                is not KnowledgeTraversalDirection.OUTGOING
                and relation.target == item
            ):
                neighbor = relation.source

            if neighbor is not None:
                neighbors.setdefault(
                    neighbor.fingerprint,
                    neighbor,
                )

        return tuple(
            sorted(
                neighbors.values(),
                key=_item_key,
            )
        )
