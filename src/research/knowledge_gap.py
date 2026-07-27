from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from hashlib import sha256

from src.research.knowledge_item import KnowledgeItem


class KnowledgeGapType(str, Enum):
    """Supported deterministic knowledge graph gaps."""

    ISOLATED_ITEM = "isolated_item"
    UNSUPPORTED_ITEM = "unsupported_item"
    UNRESOLVED_CONTRADICTION = (
        "unresolved_contradiction"
    )


def _item_key(
    item: KnowledgeItem,
) -> tuple[str, int, str]:
    return (
        item.id,
        item.version,
        item.fingerprint,
    )


def _normalize_gap_type(
    value: object,
) -> KnowledgeGapType:
    if not isinstance(value, KnowledgeGapType):
        raise TypeError(
            "gap_type must be a "
            "KnowledgeGapType"
        )

    return value


def _normalize_items(
    value: object,
) -> tuple[KnowledgeItem, ...]:
    if not isinstance(value, tuple):
        raise TypeError(
            "items must be a tuple"
        )

    if not value:
        raise ValueError(
            "items must not be empty"
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


def _normalize_applicability(
    value: object,
) -> tuple[str, ...]:
    if not isinstance(value, tuple):
        raise TypeError(
            "applicability must be a tuple"
        )

    if not value:
        raise ValueError(
            "applicability must not be empty"
        )

    normalized: list[str] = []

    for term in value:
        if not isinstance(term, str):
            raise TypeError(
                "each applicability term "
                "must be a string"
            )

        normalized_term = (
            term.strip().casefold()
        )

        if not normalized_term:
            raise ValueError(
                "applicability must not "
                "contain empty terms"
            )

        normalized.append(normalized_term)

    if len(normalized) != len(set(normalized)):
        raise ValueError(
            "applicability must not contain "
            "duplicates"
        )

    return tuple(sorted(normalized))


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


def _normalize_snapshot_fingerprint(
    value: object,
) -> str:
    if not isinstance(value, str):
        raise TypeError(
            "snapshot_fingerprint must be "
            "a string"
        )

    normalized = value.strip().lower()

    if (
        len(normalized) != 64
        or any(
            character not in "0123456789abcdef"
            for character in normalized
        )
    ):
        raise ValueError(
            "snapshot_fingerprint must be a "
            "SHA256 hexadecimal digest"
        )

    return normalized


def _validate_item_count(
    gap_type: KnowledgeGapType,
    items: tuple[KnowledgeItem, ...],
) -> None:
    expected_count = {
        KnowledgeGapType.ISOLATED_ITEM: 1,
        KnowledgeGapType.UNSUPPORTED_ITEM: 1,
        KnowledgeGapType.UNRESOLVED_CONTRADICTION: 2,
    }[gap_type]

    if len(items) != expected_count:
        raise ValueError(
            f"{gap_type.value} gap must "
            f"reference exactly {expected_count} "
            "KnowledgeItem object"
            + (
                ""
                if expected_count == 1
                else "s"
            )
        )

    if (
        gap_type
        is KnowledgeGapType.UNRESOLVED_CONTRADICTION
        and items[0].id == items[1].id
    ):
        raise ValueError(
            "unresolved_contradiction gap "
            "must reference different "
            "knowledge IDs"
        )


@dataclass(frozen=True, slots=True)
class KnowledgeGap:
    """
    Immutable gap detected in an exact knowledge graph snapshot.
    """

    gap_type: KnowledgeGapType
    items: tuple[KnowledgeItem, ...]
    applicability: tuple[str, ...]
    reason: str
    snapshot_fingerprint: str

    def __post_init__(self) -> None:
        gap_type = _normalize_gap_type(
            self.gap_type
        )
        items = _normalize_items(self.items)
        applicability = (
            _normalize_applicability(
                self.applicability
            )
        )
        reason = _normalize_reason(
            self.reason
        )
        snapshot_fingerprint = (
            _normalize_snapshot_fingerprint(
                self.snapshot_fingerprint
            )
        )

        _validate_item_count(
            gap_type,
            items,
        )

        object.__setattr__(
            self,
            "gap_type",
            gap_type,
        )
        object.__setattr__(
            self,
            "items",
            items,
        )
        object.__setattr__(
            self,
            "applicability",
            applicability,
        )
        object.__setattr__(
            self,
            "reason",
            reason,
        )
        object.__setattr__(
            self,
            "snapshot_fingerprint",
            snapshot_fingerprint,
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "gap_type": self.gap_type.value,
            "items": [
                {
                    "id": item.id,
                    "version": item.version,
                    "fingerprint": (
                        item.fingerprint
                    ),
                }
                for item in self.items
            ],
            "applicability": list(
                self.applicability
            ),
            "reason": self.reason,
            "snapshot_fingerprint": (
                self.snapshot_fingerprint
            ),
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
