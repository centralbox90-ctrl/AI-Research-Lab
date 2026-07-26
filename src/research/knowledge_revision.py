from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256

from src.research.knowledge_item import KnowledgeItem


def _normalize_valid_from(
    value: object,
) -> datetime:
    if not isinstance(value, datetime):
        raise TypeError(
            "valid_from must be a datetime"
        )

    if (
        value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise ValueError(
            "valid_from must be timezone-aware"
        )

    return value.astimezone(timezone.utc)


def _normalize_change_reason(
    value: object,
) -> str:
    if not isinstance(value, str):
        raise TypeError(
            "change_reason must be a string"
        )

    normalized = value.strip()

    if not normalized:
        raise ValueError(
            "change_reason must not be empty"
        )

    return normalized


def _normalize_supersedes_version(
    value: object,
) -> int | None:
    if value is None:
        return None

    if (
        not isinstance(value, int)
        or isinstance(value, bool)
    ):
        raise TypeError(
            "supersedes_version must be an integer "
            "or None"
        )

    if value < 1:
        raise ValueError(
            "supersedes_version must be positive"
        )

    return value


@dataclass(frozen=True, slots=True)
class KnowledgeRevision:
    """
    Immutable history record for one KnowledgeItem version.
    """

    item: KnowledgeItem
    valid_from: datetime
    change_reason: str
    supersedes_version: int | None

    def __post_init__(self) -> None:
        if not isinstance(self.item, KnowledgeItem):
            raise TypeError(
                "item must be a KnowledgeItem"
            )

        valid_from = _normalize_valid_from(
            self.valid_from
        )
        change_reason = _normalize_change_reason(
            self.change_reason
        )
        supersedes_version = (
            _normalize_supersedes_version(
                self.supersedes_version
            )
        )

        if self.item.version == 1:
            if supersedes_version is not None:
                raise ValueError(
                    "initial revision must not "
                    "supersede another version"
                )
        elif (
            supersedes_version
            != self.item.version - 1
        ):
            raise ValueError(
                "revision must supersede the "
                "immediately preceding version"
            )

        object.__setattr__(
            self,
            "valid_from",
            valid_from,
        )
        object.__setattr__(
            self,
            "change_reason",
            change_reason,
        )
        object.__setattr__(
            self,
            "supersedes_version",
            supersedes_version,
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "item": self.item.to_dict(),
            "item_fingerprint": self.item.fingerprint,
            "valid_from": (
                self.valid_from
                .isoformat()
                .replace("+00:00", "Z")
            ),
            "change_reason": self.change_reason,
            "supersedes_version": (
                self.supersedes_version
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
