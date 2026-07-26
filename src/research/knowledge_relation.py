from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from hashlib import sha256

from src.research.knowledge_item import KnowledgeItem


class KnowledgeRelationType(str, Enum):
    """Supported semantic relations between knowledge items."""

    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    EXTENDS = "extends"
    REFINES = "refines"
    SUPERSEDES = "supersedes"
    DERIVED_FROM = "derived_from"


def _normalize_item(
    value: object,
    *,
    field_name: str,
) -> KnowledgeItem:
    if not isinstance(value, KnowledgeItem):
        raise TypeError(
            f"{field_name} must be a KnowledgeItem"
        )

    return value


def _normalize_relation_type(
    value: object,
) -> KnowledgeRelationType:
    if not isinstance(
        value,
        KnowledgeRelationType,
    ):
        raise TypeError(
            "relation_type must be a "
            "KnowledgeRelationType"
        )

    return value


def _normalize_reason(
    value: object,
) -> str:
    if not isinstance(value, str):
        raise TypeError(
            "reason must be a string"
        )

    normalized = value.strip()

    if not normalized:
        raise ValueError(
            "reason must not be empty"
        )

    return normalized


def _item_key(
    item: KnowledgeItem,
) -> tuple[str, int, str]:
    return (
        item.id,
        item.version,
        item.fingerprint,
    )


@dataclass(frozen=True, slots=True)
class KnowledgeRelation:
    """
    Immutable typed edge between exact KnowledgeItem versions.
    """

    source: KnowledgeItem
    target: KnowledgeItem
    relation_type: KnowledgeRelationType
    reason: str

    def __post_init__(self) -> None:
        source = _normalize_item(
            self.source,
            field_name="source",
        )
        target = _normalize_item(
            self.target,
            field_name="target",
        )
        relation_type = _normalize_relation_type(
            self.relation_type
        )
        reason = _normalize_reason(
            self.reason
        )

        if (
            source.id == target.id
            and source.version == target.version
        ):
            raise ValueError(
                "source and target must reference "
                "different knowledge versions"
            )

        if (
            relation_type
            is KnowledgeRelationType.CONTRADICTS
            and _item_key(target) < _item_key(source)
        ):
            source, target = target, source

        object.__setattr__(
            self,
            "source",
            source,
        )
        object.__setattr__(
            self,
            "target",
            target,
        )
        object.__setattr__(
            self,
            "relation_type",
            relation_type,
        )
        object.__setattr__(
            self,
            "reason",
            reason,
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "source": {
                "id": self.source.id,
                "version": self.source.version,
                "fingerprint": (
                    self.source.fingerprint
                ),
            },
            "target": {
                "id": self.target.id,
                "version": self.target.version,
                "fingerprint": (
                    self.target.fingerprint
                ),
            },
            "relation_type": (
                self.relation_type.value
            ),
            "reason": self.reason,
        }

    @property
    def fingerprint(self) -> str:
        serialized = json.dumps(
            self.to_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )

        return sha256(
            serialized.encode("utf-8")
        ).hexdigest()
