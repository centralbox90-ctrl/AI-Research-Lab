from __future__ import annotations

import json
from dataclasses import dataclass
from hashlib import sha256
from math import isfinite
from numbers import Real


def _normalize_text(
    value: object,
    *,
    field_name: str,
) -> str:
    if not isinstance(value, str):
        raise TypeError(
            f"{field_name} must be a string"
        )

    normalized = value.strip()

    if not normalized:
        raise ValueError(
            f"{field_name} must not be empty"
        )

    return normalized


def _normalize_text_items(
    value: object,
    *,
    field_name: str,
    require_nonempty: bool = False,
) -> tuple[str, ...]:
    if not isinstance(value, tuple):
        raise TypeError(
            f"{field_name} must be a tuple"
        )

    if require_nonempty and not value:
        raise ValueError(
            f"{field_name} must not be empty"
        )

    normalized = tuple(
        _normalize_text(
            item,
            field_name=field_name,
        )
        for item in value
    )

    if len(normalized) != len(set(normalized)):
        raise ValueError(
            f"{field_name} must not contain duplicates"
        )

    return tuple(sorted(normalized))


def _normalize_confidence(
    value: object,
) -> float:
    if (
        not isinstance(value, Real)
        or isinstance(value, bool)
    ):
        raise TypeError(
            "confidence must be a real number"
        )

    normalized = float(value)

    if not isfinite(normalized):
        raise ValueError(
            "confidence must be finite"
        )

    if not 0.0 <= normalized <= 1.0:
        raise ValueError(
            "confidence must be between 0 and 1"
        )

    return normalized


def _normalize_version(
    value: object,
) -> int:
    if (
        not isinstance(value, int)
        or isinstance(value, bool)
    ):
        raise TypeError(
            "version must be an integer"
        )

    if value < 1:
        raise ValueError(
            "version must be positive"
        )

    return value


def _normalize_provenance(
    value: object,
) -> tuple[tuple[str, str], ...]:
    if not isinstance(value, tuple):
        raise TypeError(
            "provenance must be a tuple"
        )

    if not value:
        raise ValueError(
            "provenance must not be empty"
        )

    normalized: list[tuple[str, str]] = []

    for entry in value:
        if (
            not isinstance(entry, tuple)
            or len(entry) != 2
        ):
            raise TypeError(
                "each provenance entry must be "
                "a key-value tuple"
            )

        key = _normalize_text(
            entry[0],
            field_name="provenance key",
        )
        item = _normalize_text(
            entry[1],
            field_name="provenance value",
        )
        normalized.append((key, item))

    keys = tuple(
        key
        for key, _ in normalized
    )

    if len(keys) != len(set(keys)):
        raise ValueError(
            "provenance keys must be unique"
        )

    return tuple(sorted(normalized))


@dataclass(frozen=True, slots=True)
class KnowledgeItem:
    """
    Immutable, versioned statement admitted to Knowledge storage.
    """

    id: str
    statement: str
    confidence: float
    applicability: tuple[str, ...]
    limitations: tuple[str, ...]
    supporting_findings: tuple[str, ...]
    version: int
    provenance: tuple[tuple[str, str], ...]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "id",
            _normalize_text(
                self.id,
                field_name="id",
            ),
        )
        object.__setattr__(
            self,
            "statement",
            _normalize_text(
                self.statement,
                field_name="statement",
            ),
        )
        object.__setattr__(
            self,
            "confidence",
            _normalize_confidence(
                self.confidence
            ),
        )
        object.__setattr__(
            self,
            "applicability",
            _normalize_text_items(
                self.applicability,
                field_name="applicability",
                require_nonempty=True,
            ),
        )
        object.__setattr__(
            self,
            "limitations",
            _normalize_text_items(
                self.limitations,
                field_name="limitations",
            ),
        )
        object.__setattr__(
            self,
            "supporting_findings",
            _normalize_text_items(
                self.supporting_findings,
                field_name="supporting_findings",
                require_nonempty=True,
            ),
        )
        object.__setattr__(
            self,
            "version",
            _normalize_version(
                self.version
            ),
        )
        object.__setattr__(
            self,
            "provenance",
            _normalize_provenance(
                self.provenance
            ),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "id": self.id,
            "statement": self.statement,
            "confidence": self.confidence,
            "applicability": list(
                self.applicability
            ),
            "limitations": list(
                self.limitations
            ),
            "supporting_findings": list(
                self.supporting_findings
            ),
            "version": self.version,
            "provenance": {
                key: value
                for key, value in self.provenance
            },
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
