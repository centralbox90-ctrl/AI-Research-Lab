from __future__ import annotations

import json
from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from src.research.knowledge_item import KnowledgeItem


class ApplicabilityMatchMode(StrEnum):
    """Matching rule for applicability query terms."""

    ALL = "all"
    ANY = "any"


def _normalize_terms(
    value: object,
) -> tuple[str, ...]:
    if not isinstance(value, tuple):
        raise TypeError(
            "terms must be a tuple"
        )

    if not value:
        raise ValueError(
            "terms must not be empty"
        )

    normalized: list[str] = []

    for term in value:
        if not isinstance(term, str):
            raise TypeError(
                "each term must be a string"
            )

        normalized_term = term.strip().casefold()

        if not normalized_term:
            raise ValueError(
                "terms must not contain empty values"
            )

        normalized.append(normalized_term)

    if len(normalized) != len(set(normalized)):
        raise ValueError(
            "terms must not contain duplicates"
        )

    return tuple(sorted(normalized))


@dataclass(frozen=True, slots=True)
class KnowledgeApplicabilityQuery:
    """
    Immutable query over KnowledgeItem applicability terms.
    """

    terms: tuple[str, ...]
    match_mode: ApplicabilityMatchMode = (
        ApplicabilityMatchMode.ALL
    )

    def __post_init__(self) -> None:
        if not isinstance(
            self.match_mode,
            ApplicabilityMatchMode,
        ):
            raise TypeError(
                "match_mode must be an "
                "ApplicabilityMatchMode"
            )

        object.__setattr__(
            self,
            "terms",
            _normalize_terms(self.terms),
        )

    def matches(
        self,
        item: KnowledgeItem,
    ) -> bool:
        if not isinstance(item, KnowledgeItem):
            raise TypeError(
                "item must be a KnowledgeItem"
            )

        item_terms = {
            term.casefold()
            for term in item.applicability
        }
        query_terms = set(self.terms)

        if (
            self.match_mode
            is ApplicabilityMatchMode.ALL
        ):
            return query_terms.issubset(item_terms)

        return not query_terms.isdisjoint(
            item_terms
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "terms": list(self.terms),
            "match_mode": self.match_mode.value,
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
