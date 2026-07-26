from __future__ import annotations

import json
from dataclasses import dataclass, field
from hashlib import sha256

from src.research.knowledge_item import KnowledgeItem


def _normalize_items(
    value: object,
) -> tuple[KnowledgeItem, KnowledgeItem]:
    if not isinstance(value, tuple):
        raise TypeError(
            "items must be a tuple"
        )

    if len(value) != 2:
        raise ValueError(
            "items must contain exactly two "
            "KnowledgeItem objects"
        )

    left, right = value

    if (
        not isinstance(left, KnowledgeItem)
        or not isinstance(right, KnowledgeItem)
    ):
        raise TypeError(
            "each item must be a KnowledgeItem"
        )

    if left.id == right.id:
        raise ValueError(
            "items must reference different "
            "knowledge IDs"
        )

    left_key = (
        left.id,
        left.version,
        left.fingerprint,
    )
    right_key = (
        right.id,
        right.version,
        right.fingerprint,
    )

    if left_key <= right_key:
        return (left, right)

    return (right, left)


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


def _resolve_conflicting_applicability(
    items: tuple[KnowledgeItem, KnowledgeItem],
) -> tuple[str, ...]:
    left, right = items
    left_terms = {
        term.casefold()
        for term in left.applicability
    }
    right_terms = {
        term.casefold()
        for term in right.applicability
    }
    overlap = tuple(
        sorted(left_terms & right_terms)
    )

    if not overlap:
        raise ValueError(
            "items must have overlapping applicability"
        )

    return overlap


@dataclass(frozen=True, slots=True)
class KnowledgeContradiction:
    """
    Immutable registration of a conflict between two knowledge items.
    """

    items: tuple[KnowledgeItem, KnowledgeItem]
    reason: str
    conflicting_applicability: tuple[
        str,
        ...,
    ] = field(init=False)

    def __post_init__(self) -> None:
        items = _normalize_items(self.items)
        reason = _normalize_reason(self.reason)
        conflicting_applicability = (
            _resolve_conflicting_applicability(
                items
            )
        )

        object.__setattr__(
            self,
            "items",
            items,
        )
        object.__setattr__(
            self,
            "reason",
            reason,
        )
        object.__setattr__(
            self,
            "conflicting_applicability",
            conflicting_applicability,
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "items": [
                {
                    "id": item.id,
                    "version": item.version,
                    "fingerprint": item.fingerprint,
                }
                for item in self.items
            ],
            "conflicting_applicability": list(
                self.conflicting_applicability
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
