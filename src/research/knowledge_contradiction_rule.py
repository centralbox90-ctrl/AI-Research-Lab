from __future__ import annotations

import json
from dataclasses import dataclass
from hashlib import sha256

from src.research.knowledge_item import KnowledgeItem


def _normalize_statements(
    value: object,
) -> tuple[str, str]:
    if not isinstance(value, tuple):
        raise TypeError(
            "statements must be a tuple"
        )

    if len(value) != 2:
        raise ValueError(
            "statements must contain exactly "
            "two values"
        )

    normalized: list[str] = []

    for statement in value:
        if not isinstance(statement, str):
            raise TypeError(
                "each statement must be a string"
            )

        normalized_statement = (
            statement.strip().casefold()
        )

        if not normalized_statement:
            raise ValueError(
                "statements must not contain "
                "empty values"
            )

        normalized.append(normalized_statement)

    if normalized[0] == normalized[1]:
        raise ValueError(
            "statements must be different"
        )

    left, right = sorted(normalized)
    return (left, right)


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


@dataclass(frozen=True, slots=True)
class KnowledgeContradictionRule:
    """
    Explicit deterministic rule for two incompatible statements.
    """

    statements: tuple[str, str]
    reason: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "statements",
            _normalize_statements(
                self.statements
            ),
        )
        object.__setattr__(
            self,
            "reason",
            _normalize_reason(self.reason),
        )

    def matches(
        self,
        left: KnowledgeItem,
        right: KnowledgeItem,
    ) -> bool:
        if (
            not isinstance(left, KnowledgeItem)
            or not isinstance(right, KnowledgeItem)
        ):
            raise TypeError(
                "left and right must be "
                "KnowledgeItem objects"
            )

        statements = tuple(
            sorted(
                (
                    left.statement.casefold(),
                    right.statement.casefold(),
                )
            )
        )

        return statements == self.statements

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "statements": list(self.statements),
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
