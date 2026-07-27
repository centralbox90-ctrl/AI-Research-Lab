from __future__ import annotations

import json
from dataclasses import dataclass
from hashlib import sha256

from src.research.knowledge_graph import (
    KnowledgeGraph,
)
from src.research.knowledge_item import KnowledgeItem
from src.research.knowledge_relation import (
    KnowledgeRelation,
)


def _item_key(
    item: KnowledgeItem,
) -> tuple[str, int, str]:
    return (
        item.id,
        item.version,
        item.fingerprint,
    )


def _relation_key(
    relation: KnowledgeRelation,
) -> tuple[object, ...]:
    return (
        *_item_key(relation.source),
        relation.relation_type.value,
        *_item_key(relation.target),
        relation.reason,
        relation.fingerprint,
    )


def _normalize_items(
    value: object,
) -> tuple[KnowledgeItem, ...]:
    if not isinstance(value, tuple):
        raise TypeError(
            "items must be a tuple"
        )

    normalized: list[KnowledgeItem] = []

    for item in value:
        if not isinstance(item, KnowledgeItem):
            raise TypeError(
                "each item must be a "
                "KnowledgeItem"
            )

        normalized.append(item)

    fingerprints = tuple(
        item.fingerprint
        for item in normalized
    )

    if (
        len(fingerprints)
        != len(set(fingerprints))
    ):
        raise ValueError(
            "items must not contain duplicate "
            "fingerprints"
        )

    versions: dict[
        tuple[str, int],
        str,
    ] = {}

    for item in normalized:
        version_key = (
            item.id,
            item.version,
        )
        existing_fingerprint = versions.get(
            version_key
        )

        if (
            existing_fingerprint is not None
            and existing_fingerprint
            != item.fingerprint
        ):
            raise ValueError(
                "items must not contain "
                "conflicting knowledge versions"
            )

        versions[version_key] = (
            item.fingerprint
        )

    return tuple(
        sorted(
            normalized,
            key=_item_key,
        )
    )


def _normalize_relations(
    value: object,
) -> tuple[KnowledgeRelation, ...]:
    if not isinstance(value, tuple):
        raise TypeError(
            "relations must be a tuple"
        )

    normalized: list[
        KnowledgeRelation
    ] = []

    for relation in value:
        if not isinstance(
            relation,
            KnowledgeRelation,
        ):
            raise TypeError(
                "each relation must be a "
                "KnowledgeRelation"
            )

        normalized.append(relation)

    fingerprints = tuple(
        relation.fingerprint
        for relation in normalized
    )

    if (
        len(fingerprints)
        != len(set(fingerprints))
    ):
        raise ValueError(
            "relations must not contain "
            "duplicate fingerprints"
        )

    return tuple(
        sorted(
            normalized,
            key=_relation_key,
        )
    )


@dataclass(frozen=True, slots=True)
class KnowledgeGraphSnapshot:
    """
    Immutable deterministic snapshot of knowledge graph state.
    """

    items: tuple[KnowledgeItem, ...]
    relations: tuple[KnowledgeRelation, ...]

    def __post_init__(self) -> None:
        items = _normalize_items(self.items)
        relations = _normalize_relations(
            self.relations
        )
        item_keys = {
            _item_key(item)
            for item in items
        }

        for relation in relations:
            if (
                _item_key(relation.source)
                not in item_keys
                or _item_key(relation.target)
                not in item_keys
            ):
                raise ValueError(
                    "relation endpoints must "
                    "reference snapshot items"
                )

        object.__setattr__(
            self,
            "items",
            items,
        )
        object.__setattr__(
            self,
            "relations",
            relations,
        )

    @classmethod
    def from_graph(
        cls,
        graph: KnowledgeGraph,
    ) -> KnowledgeGraphSnapshot:
        if not isinstance(graph, KnowledgeGraph):
            raise TypeError(
                "graph must be a KnowledgeGraph"
            )

        relations = graph.relations()
        items_by_fingerprint: dict[
            str,
            KnowledgeItem,
        ] = {}

        for relation in relations:
            items_by_fingerprint.setdefault(
                relation.source.fingerprint,
                relation.source,
            )
            items_by_fingerprint.setdefault(
                relation.target.fingerprint,
                relation.target,
            )

        return cls(
            items=tuple(
                items_by_fingerprint.values()
            ),
            relations=relations,
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "items": [
                {
                    **item.to_dict(),
                    "fingerprint": (
                        item.fingerprint
                    ),
                }
                for item in self.items
            ],
            "relations": [
                relation.to_dict()
                for relation in self.relations
            ],
        }

    def to_json(self) -> str:
        return json.dumps(
            self.to_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )

    @property
    def fingerprint(self) -> str:
        return sha256(
            self.to_json().encode("utf-8")
        ).hexdigest()
