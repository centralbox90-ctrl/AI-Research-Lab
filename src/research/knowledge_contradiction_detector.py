from __future__ import annotations

from itertools import combinations

from src.research.knowledge_contradiction import (
    KnowledgeContradiction,
)
from src.research.knowledge_contradiction_rule import (
    KnowledgeContradictionRule,
)
from src.research.knowledge_item import KnowledgeItem
from src.research.knowledge_repository import (
    KnowledgeRepository,
)


def _normalize_rules(
    value: object,
) -> tuple[KnowledgeContradictionRule, ...]:
    if not isinstance(value, tuple):
        raise TypeError(
            "rules must be a tuple"
        )

    for rule in value:
        if not isinstance(
            rule,
            KnowledgeContradictionRule,
        ):
            raise TypeError(
                "each rule must be a "
                "KnowledgeContradictionRule"
            )

    statement_pairs = tuple(
        rule.statements
        for rule in value
    )

    if len(statement_pairs) != len(
        set(statement_pairs)
    ):
        raise ValueError(
            "rules must not contain duplicate "
            "statement pairs"
        )

    return tuple(
        sorted(
            value,
            key=lambda rule: (
                rule.statements,
                rule.reason,
                rule.fingerprint,
            ),
        )
    )


def _normalize_repository_items(
    value: object,
) -> tuple[KnowledgeItem, ...]:
    if not isinstance(value, tuple):
        raise TypeError(
            "repository list_all must return a tuple"
        )

    for item in value:
        if not isinstance(item, KnowledgeItem):
            raise TypeError(
                "repository items must be "
                "KnowledgeItem objects"
            )

    item_ids = tuple(
        item.id
        for item in value
    )

    if len(item_ids) != len(set(item_ids)):
        raise ValueError(
            "repository must return at most one "
            "version per knowledge ID"
        )

    return tuple(
        sorted(
            value,
            key=lambda item: (
                item.id,
                item.version,
                item.fingerprint,
            ),
        )
    )


def _has_applicability_overlap(
    left: KnowledgeItem,
    right: KnowledgeItem,
) -> bool:
    left_terms = {
        term.casefold()
        for term in left.applicability
    }
    right_terms = {
        term.casefold()
        for term in right.applicability
    }

    return not left_terms.isdisjoint(
        right_terms
    )


class KnowledgeContradictionDetector:
    """
    Applies explicit contradiction rules to latest repository items.
    """

    def detect(
        self,
        *,
        repository: KnowledgeRepository,
        rules: tuple[
            KnowledgeContradictionRule,
            ...,
        ],
    ) -> tuple[KnowledgeContradiction, ...]:
        if not isinstance(
            repository,
            KnowledgeRepository,
        ):
            raise TypeError(
                "repository must implement "
                "KnowledgeRepository"
            )

        normalized_rules = _normalize_rules(
            rules
        )
        items = _normalize_repository_items(
            repository.list_all()
        )
        contradictions: list[
            KnowledgeContradiction
        ] = []

        for left, right in combinations(items, 2):
            if not _has_applicability_overlap(
                left,
                right,
            ):
                continue

            for rule in normalized_rules:
                if not rule.matches(left, right):
                    continue

                contradictions.append(
                    KnowledgeContradiction(
                        items=(left, right),
                        reason=rule.reason,
                    )
                )
                break

        return tuple(contradictions)
