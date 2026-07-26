from dataclasses import FrozenInstanceError

import pytest

from src.research.knowledge_contradiction import (
    KnowledgeContradiction,
)
from src.research.knowledge_item import KnowledgeItem


def build_item(
    *,
    item_id: str,
    statement: str,
    version: int = 1,
    applicability: tuple[str, ...] = (
        "liquid markets",
    ),
) -> KnowledgeItem:
    return KnowledgeItem(
        id=item_id,
        statement=statement,
        confidence=0.85,
        applicability=applicability,
        limitations=("limited history",),
        supporting_findings=(
            f"{item_id}-finding-a",
        ),
        version=version,
        provenance=(
            ("source", f"{item_id}-source"),
        ),
    )


def test_canonicalizes_items_reason_and_applicability(
) -> None:
    item_b = build_item(
        item_id="knowledge-b",
        statement="Momentum does not persist.",
        applicability=(
            "Trend Regime",
            "Liquid Markets",
        ),
    )
    item_a = build_item(
        item_id="knowledge-a",
        statement="Momentum persists.",
        applicability=(
            "liquid markets",
            "trend regime",
        ),
    )

    contradiction = KnowledgeContradiction(
        items=(item_b, item_a),
        reason="  Opposing conclusions.  ",
    )

    assert contradiction.items == (
        item_a,
        item_b,
    )
    assert contradiction.reason == (
        "Opposing conclusions."
    )
    assert (
        contradiction.conflicting_applicability
        == (
            "liquid markets",
            "trend regime",
        )
    )


def test_serializes_versioned_item_references(
) -> None:
    item_a = build_item(
        item_id="knowledge-a",
        statement="Momentum persists.",
        version=2,
    )
    item_b = build_item(
        item_id="knowledge-b",
        statement="Momentum does not persist.",
        version=3,
    )
    contradiction = KnowledgeContradiction(
        items=(item_a, item_b),
        reason="Opposing conclusions.",
    )

    assert contradiction.to_dict() == {
        "schema_version": 1,
        "items": [
            {
                "id": "knowledge-a",
                "version": 2,
                "fingerprint": item_a.fingerprint,
            },
            {
                "id": "knowledge-b",
                "version": 3,
                "fingerprint": item_b.fingerprint,
            },
        ],
        "conflicting_applicability": [
            "liquid markets",
        ],
        "reason": "Opposing conclusions.",
    }


def test_fingerprint_is_independent_of_item_order(
) -> None:
    item_a = build_item(
        item_id="knowledge-a",
        statement="Momentum persists.",
    )
    item_b = build_item(
        item_id="knowledge-b",
        statement="Momentum does not persist.",
    )

    first = KnowledgeContradiction(
        items=(item_a, item_b),
        reason="Opposing conclusions.",
    )
    second = KnowledgeContradiction(
        items=(item_b, item_a),
        reason="Opposing conclusions.",
    )

    assert first == second
    assert first.fingerprint == second.fingerprint
    assert len(first.fingerprint) == 64


def test_fingerprint_changes_with_reason(
) -> None:
    item_a = build_item(
        item_id="knowledge-a",
        statement="Momentum persists.",
    )
    item_b = build_item(
        item_id="knowledge-b",
        statement="Momentum does not persist.",
    )

    first = KnowledgeContradiction(
        items=(item_a, item_b),
        reason="Opposing conclusions.",
    )
    second = KnowledgeContradiction(
        items=(item_a, item_b),
        reason="Opposing robust conclusions.",
    )

    assert first.fingerprint != second.fingerprint


def test_is_immutable() -> None:
    item_a = build_item(
        item_id="knowledge-a",
        statement="Momentum persists.",
    )
    item_b = build_item(
        item_id="knowledge-b",
        statement="Momentum does not persist.",
    )
    contradiction = KnowledgeContradiction(
        items=(item_a, item_b),
        reason="Opposing conclusions.",
    )

    with pytest.raises(FrozenInstanceError):
        contradiction.reason = "Changed"  # type: ignore[misc]


@pytest.mark.parametrize(
    "items",
    (
        [],
        {"knowledge-a", "knowledge-b"},
    ),
)
def test_rejects_non_tuple_items(
    items: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="items must be a tuple",
    ):
        KnowledgeContradiction(
            items=items,  # type: ignore[arg-type]
            reason="Opposing conclusions.",
        )


@pytest.mark.parametrize(
    "items",
    (
        (),
        (
            build_item(
                item_id="knowledge-a",
                statement="Statement A.",
            ),
        ),
        (
            build_item(
                item_id="knowledge-a",
                statement="Statement A.",
            ),
            build_item(
                item_id="knowledge-b",
                statement="Statement B.",
            ),
            build_item(
                item_id="knowledge-c",
                statement="Statement C.",
            ),
        ),
    ),
)
def test_requires_exactly_two_items(
    items: tuple[KnowledgeItem, ...],
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "items must contain exactly two "
            "KnowledgeItem objects"
        ),
    ):
        KnowledgeContradiction(
            items=items,  # type: ignore[arg-type]
            reason="Opposing conclusions.",
        )


def test_rejects_non_knowledge_item() -> None:
    item = build_item(
        item_id="knowledge-a",
        statement="Statement A.",
    )

    with pytest.raises(
        TypeError,
        match="each item must be a KnowledgeItem",
    ):
        KnowledgeContradiction(
            items=(item, object()),  # type: ignore[arg-type]
            reason="Opposing conclusions.",
        )


def test_rejects_same_knowledge_id() -> None:
    first = build_item(
        item_id="knowledge-a",
        statement="Statement A.",
        version=1,
    )
    second = build_item(
        item_id="knowledge-a",
        statement="Updated statement A.",
        version=2,
    )

    with pytest.raises(
        ValueError,
        match=(
            "items must reference different "
            "knowledge IDs"
        ),
    ):
        KnowledgeContradiction(
            items=(first, second),
            reason="Opposing conclusions.",
        )


def test_requires_overlapping_applicability(
) -> None:
    item_a = build_item(
        item_id="knowledge-a",
        statement="Statement A.",
        applicability=("trend regime",),
    )
    item_b = build_item(
        item_id="knowledge-b",
        statement="Statement B.",
        applicability=("range regime",),
    )

    with pytest.raises(
        ValueError,
        match=(
            "items must have overlapping applicability"
        ),
    ):
        KnowledgeContradiction(
            items=(item_a, item_b),
            reason="Opposing conclusions.",
        )


@pytest.mark.parametrize(
    "reason",
    (
        None,
        1,
        True,
    ),
)
def test_rejects_non_string_reason(
    reason: object,
) -> None:
    item_a = build_item(
        item_id="knowledge-a",
        statement="Statement A.",
    )
    item_b = build_item(
        item_id="knowledge-b",
        statement="Statement B.",
    )

    with pytest.raises(
        TypeError,
        match="reason must be a string",
    ):
        KnowledgeContradiction(
            items=(item_a, item_b),
            reason=reason,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "reason",
    (
        "",
        "   ",
    ),
)
def test_rejects_empty_reason(
    reason: str,
) -> None:
    item_a = build_item(
        item_id="knowledge-a",
        statement="Statement A.",
    )
    item_b = build_item(
        item_id="knowledge-b",
        statement="Statement B.",
    )

    with pytest.raises(
        ValueError,
        match="reason must not be empty",
    ):
        KnowledgeContradiction(
            items=(item_a, item_b),
            reason=reason,
        )
