from dataclasses import FrozenInstanceError

import pytest

from src.research.knowledge_contradiction_rule import (
    KnowledgeContradictionRule,
)
from src.research.knowledge_item import KnowledgeItem


def build_item(
    *,
    item_id: str,
    statement: str,
) -> KnowledgeItem:
    return KnowledgeItem(
        id=item_id,
        statement=statement,
        confidence=0.85,
        applicability=("liquid markets",),
        limitations=("limited history",),
        supporting_findings=(
            f"{item_id}-finding-a",
        ),
        version=1,
        provenance=(
            ("source", f"{item_id}-source"),
        ),
    )


def test_normalizes_statements_and_reason(
) -> None:
    rule = KnowledgeContradictionRule(
        statements=(
            "  Momentum Persists. ",
            "MOMENTUM DOES NOT PERSIST.",
        ),
        reason="  Opposing conclusions.  ",
    )

    assert rule.statements == (
        "momentum does not persist.",
        "momentum persists.",
    )
    assert rule.reason == "Opposing conclusions."


def test_matches_items_in_either_order(
) -> None:
    rule = KnowledgeContradictionRule(
        statements=(
            "Momentum persists.",
            "Momentum does not persist.",
        ),
        reason="Opposing conclusions.",
    )
    positive = build_item(
        item_id="knowledge-positive",
        statement="MOMENTUM PERSISTS.",
    )
    negative = build_item(
        item_id="knowledge-negative",
        statement="Momentum does not persist.",
    )

    assert rule.matches(positive, negative) is True
    assert rule.matches(negative, positive) is True


def test_does_not_match_other_statements(
) -> None:
    rule = KnowledgeContradictionRule(
        statements=(
            "Momentum persists.",
            "Momentum does not persist.",
        ),
        reason="Opposing conclusions.",
    )
    positive = build_item(
        item_id="knowledge-positive",
        statement="Momentum persists.",
    )
    unrelated = build_item(
        item_id="knowledge-unrelated",
        statement="Volatility clusters.",
    )

    assert rule.matches(positive, unrelated) is False


def test_serializes_normalized_rule(
) -> None:
    rule = KnowledgeContradictionRule(
        statements=(
            "Momentum persists.",
            "Momentum does not persist.",
        ),
        reason="Opposing conclusions.",
    )

    assert rule.to_dict() == {
        "schema_version": 1,
        "statements": [
            "momentum does not persist.",
            "momentum persists.",
        ],
        "reason": "Opposing conclusions.",
    }


def test_fingerprint_is_independent_of_order_and_case(
) -> None:
    first = KnowledgeContradictionRule(
        statements=(
            "Momentum persists.",
            "Momentum does not persist.",
        ),
        reason="Opposing conclusions.",
    )
    second = KnowledgeContradictionRule(
        statements=(
            "MOMENTUM DOES NOT PERSIST.",
            "momentum persists.",
        ),
        reason="Opposing conclusions.",
    )

    assert first == second
    assert first.fingerprint == second.fingerprint
    assert len(first.fingerprint) == 64


def test_fingerprint_changes_with_reason(
) -> None:
    first = KnowledgeContradictionRule(
        statements=(
            "Momentum persists.",
            "Momentum does not persist.",
        ),
        reason="Opposing conclusions.",
    )
    second = KnowledgeContradictionRule(
        statements=first.statements,
        reason="Opposing robust conclusions.",
    )

    assert first.fingerprint != second.fingerprint


def test_is_immutable() -> None:
    rule = KnowledgeContradictionRule(
        statements=(
            "Momentum persists.",
            "Momentum does not persist.",
        ),
        reason="Opposing conclusions.",
    )

    with pytest.raises(FrozenInstanceError):
        rule.reason = "Changed"  # type: ignore[misc]


@pytest.mark.parametrize(
    ("left", "right"),
    (
        (object(), object()),
        (
            build_item(
                item_id="knowledge-a",
                statement="Statement A.",
            ),
            object(),
        ),
    ),
)
def test_matches_rejects_non_knowledge_items(
    left: object,
    right: object,
) -> None:
    rule = KnowledgeContradictionRule(
        statements=(
            "Statement A.",
            "Statement B.",
        ),
        reason="Opposing conclusions.",
    )

    with pytest.raises(
        TypeError,
        match=(
            "left and right must be "
            "KnowledgeItem objects"
        ),
    ):
        rule.matches(
            left,  # type: ignore[arg-type]
            right,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "statements",
    (
        [],
        {"Statement A.", "Statement B."},
    ),
)
def test_rejects_non_tuple_statements(
    statements: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="statements must be a tuple",
    ):
        KnowledgeContradictionRule(
            statements=statements,  # type: ignore[arg-type]
            reason="Opposing conclusions.",
        )


@pytest.mark.parametrize(
    "statements",
    (
        (),
        ("Statement A.",),
        (
            "Statement A.",
            "Statement B.",
            "Statement C.",
        ),
    ),
)
def test_requires_exactly_two_statements(
    statements: tuple[str, ...],
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "statements must contain exactly "
            "two values"
        ),
    ):
        KnowledgeContradictionRule(
            statements=statements,  # type: ignore[arg-type]
            reason="Opposing conclusions.",
        )


def test_rejects_non_string_statement(
) -> None:
    with pytest.raises(
        TypeError,
        match="each statement must be a string",
    ):
        KnowledgeContradictionRule(
            statements=(
                "Statement A.",
                object(),  # type: ignore[arg-type]
            ),
            reason="Opposing conclusions.",
        )


@pytest.mark.parametrize(
    "statement",
    (
        "",
        "   ",
    ),
)
def test_rejects_empty_statement(
    statement: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "statements must not contain "
            "empty values"
        ),
    ):
        KnowledgeContradictionRule(
            statements=(
                "Statement A.",
                statement,
            ),
            reason="Opposing conclusions.",
        )


def test_requires_different_statements(
) -> None:
    with pytest.raises(
        ValueError,
        match="statements must be different",
    ):
        KnowledgeContradictionRule(
            statements=(
                "Statement A.",
                " statement a. ",
            ),
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
    with pytest.raises(
        TypeError,
        match="reason must be a string",
    ):
        KnowledgeContradictionRule(
            statements=(
                "Statement A.",
                "Statement B.",
            ),
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
    with pytest.raises(
        ValueError,
        match="reason must not be empty",
    ):
        KnowledgeContradictionRule(
            statements=(
                "Statement A.",
                "Statement B.",
            ),
            reason=reason,
        )
