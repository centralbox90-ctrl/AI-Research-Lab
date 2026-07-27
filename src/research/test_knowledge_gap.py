from dataclasses import FrozenInstanceError

import pytest

from src.research.knowledge_gap import (
    KnowledgeGap,
    KnowledgeGapType,
)
from src.research.knowledge_item import KnowledgeItem


SNAPSHOT_FINGERPRINT = "a" * 64


def build_item(
    item_id: str,
    *,
    version: int = 1,
    statement: str | None = None,
) -> KnowledgeItem:
    return KnowledgeItem(
        id=item_id,
        statement=(
            statement
            or f"Statement {item_id}."
        ),
        confidence=0.85,
        applicability=(
            "liquid markets",
        ),
        limitations=(
            "limited history",
        ),
        supporting_findings=(
            f"{item_id}-finding-a",
        ),
        version=version,
        provenance=(
            (
                "source",
                f"{item_id}-source",
            ),
        ),
    )


def test_exposes_supported_gap_types() -> None:
    assert tuple(
        gap_type.value
        for gap_type in KnowledgeGapType
    ) == (
        "isolated_item",
        "unsupported_item",
        "unresolved_contradiction",
    )


def test_normalizes_isolated_gap() -> None:
    item = build_item("knowledge-a")

    gap = KnowledgeGap(
        gap_type=KnowledgeGapType.ISOLATED_ITEM,
        items=(item,),
        applicability=(
            " Trending Markets ",
            "LIQUID MARKETS",
        ),
        reason=" No graph relations. ",
        snapshot_fingerprint=(
            SNAPSHOT_FINGERPRINT.upper()
        ),
    )

    assert gap.gap_type is (
        KnowledgeGapType.ISOLATED_ITEM
    )
    assert gap.items == (item,)
    assert gap.applicability == (
        "liquid markets",
        "trending markets",
    )
    assert gap.reason == "No graph relations."
    assert gap.snapshot_fingerprint == (
        SNAPSHOT_FINGERPRINT
    )


def test_canonicalizes_contradiction_items(
) -> None:
    item_a = build_item("knowledge-a")
    item_b = build_item("knowledge-b")

    gap = KnowledgeGap(
        gap_type=(
            KnowledgeGapType
            .UNRESOLVED_CONTRADICTION
        ),
        items=(item_b, item_a),
        applicability=(
            "liquid markets",
        ),
        reason="Conflict is unresolved.",
        snapshot_fingerprint=(
            SNAPSHOT_FINGERPRINT
        ),
    )

    assert gap.items == (
        item_a,
        item_b,
    )


def test_serializes_exact_references() -> None:
    item_a = build_item("knowledge-a")
    item_b = build_item("knowledge-b")
    gap = KnowledgeGap(
        gap_type=(
            KnowledgeGapType
            .UNRESOLVED_CONTRADICTION
        ),
        items=(item_a, item_b),
        applicability=(
            "liquid markets",
        ),
        reason="Conflict is unresolved.",
        snapshot_fingerprint=(
            SNAPSHOT_FINGERPRINT
        ),
    )

    assert gap.to_dict() == {
        "schema_version": 1,
        "gap_type": (
            "unresolved_contradiction"
        ),
        "items": [
            {
                "id": item_a.id,
                "version": item_a.version,
                "fingerprint": (
                    item_a.fingerprint
                ),
            },
            {
                "id": item_b.id,
                "version": item_b.version,
                "fingerprint": (
                    item_b.fingerprint
                ),
            },
        ],
        "applicability": [
            "liquid markets",
        ],
        "reason": "Conflict is unresolved.",
        "snapshot_fingerprint": (
            SNAPSHOT_FINGERPRINT
        ),
    }


def test_fingerprint_is_order_independent(
) -> None:
    item_a = build_item("knowledge-a")
    item_b = build_item("knowledge-b")

    first = KnowledgeGap(
        gap_type=(
            KnowledgeGapType
            .UNRESOLVED_CONTRADICTION
        ),
        items=(item_a, item_b),
        applicability=(
            "trending markets",
            "liquid markets",
        ),
        reason="Conflict is unresolved.",
        snapshot_fingerprint=(
            SNAPSHOT_FINGERPRINT
        ),
    )
    second = KnowledgeGap(
        gap_type=(
            KnowledgeGapType
            .UNRESOLVED_CONTRADICTION
        ),
        items=(item_b, item_a),
        applicability=(
            "LIQUID MARKETS",
            "TRENDING MARKETS",
        ),
        reason="Conflict is unresolved.",
        snapshot_fingerprint=(
            SNAPSHOT_FINGERPRINT
        ),
    )

    assert first.fingerprint == (
        second.fingerprint
    )
    assert len(first.fingerprint) == 64


def test_fingerprint_changes_with_gap_type(
) -> None:
    item = build_item("knowledge-a")
    isolated = KnowledgeGap(
        gap_type=KnowledgeGapType.ISOLATED_ITEM,
        items=(item,),
        applicability=(
            "liquid markets",
        ),
        reason="Needs graph connections.",
        snapshot_fingerprint=(
            SNAPSHOT_FINGERPRINT
        ),
    )
    unsupported = KnowledgeGap(
        gap_type=(
            KnowledgeGapType.UNSUPPORTED_ITEM
        ),
        items=(item,),
        applicability=(
            "liquid markets",
        ),
        reason="Needs graph connections.",
        snapshot_fingerprint=(
            SNAPSHOT_FINGERPRINT
        ),
    )

    assert isolated.fingerprint != (
        unsupported.fingerprint
    )


def test_gap_is_immutable() -> None:
    gap = KnowledgeGap(
        gap_type=KnowledgeGapType.ISOLATED_ITEM,
        items=(build_item("knowledge-a"),),
        applicability=(
            "liquid markets",
        ),
        reason="No graph relations.",
        snapshot_fingerprint=(
            SNAPSHOT_FINGERPRINT
        ),
    )

    with pytest.raises(FrozenInstanceError):
        gap.reason = "Changed."  # type: ignore[misc]


@pytest.mark.parametrize(
    "gap_type",
    (
        "isolated_item",
        None,
        1,
    ),
)
def test_rejects_invalid_gap_type(
    gap_type: object,
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "gap_type must be a "
            "KnowledgeGapType"
        ),
    ):
        KnowledgeGap(
            gap_type=gap_type,  # type: ignore[arg-type]
            items=(build_item("knowledge-a"),),
            applicability=(
                "liquid markets",
            ),
            reason="No graph relations.",
            snapshot_fingerprint=(
                SNAPSHOT_FINGERPRINT
            ),
        )


@pytest.mark.parametrize(
    "items",
    (
        [],
        set(),
        None,
    ),
)
def test_rejects_non_tuple_items(
    items: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="items must be a tuple",
    ):
        KnowledgeGap(
            gap_type=(
                KnowledgeGapType.ISOLATED_ITEM
            ),
            items=items,  # type: ignore[arg-type]
            applicability=(
                "liquid markets",
            ),
            reason="No graph relations.",
            snapshot_fingerprint=(
                SNAPSHOT_FINGERPRINT
            ),
        )


def test_rejects_empty_items() -> None:
    with pytest.raises(
        ValueError,
        match="items must not be empty",
    ):
        KnowledgeGap(
            gap_type=(
                KnowledgeGapType.ISOLATED_ITEM
            ),
            items=(),
            applicability=(
                "liquid markets",
            ),
            reason="No graph relations.",
            snapshot_fingerprint=(
                SNAPSHOT_FINGERPRINT
            ),
        )


def test_rejects_non_knowledge_item(
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "each item must be a "
            "KnowledgeItem"
        ),
    ):
        KnowledgeGap(
            gap_type=(
                KnowledgeGapType.ISOLATED_ITEM
            ),
            items=(
                object(),  # type: ignore[arg-type]
            ),
            applicability=(
                "liquid markets",
            ),
            reason="No graph relations.",
            snapshot_fingerprint=(
                SNAPSHOT_FINGERPRINT
            ),
        )


def test_rejects_duplicate_item_fingerprint(
) -> None:
    item = build_item("knowledge-a")

    with pytest.raises(
        ValueError,
        match=(
            "items must not contain duplicate "
            "fingerprints"
        ),
    ):
        KnowledgeGap(
            gap_type=(
                KnowledgeGapType
                .UNRESOLVED_CONTRADICTION
            ),
            items=(item, item),
            applicability=(
                "liquid markets",
            ),
            reason="Conflict is unresolved.",
            snapshot_fingerprint=(
                SNAPSHOT_FINGERPRINT
            ),
        )


def test_rejects_conflicting_knowledge_version(
) -> None:
    first = build_item(
        "knowledge-a",
        statement="First statement.",
    )
    second = build_item(
        "knowledge-a",
        statement="Second statement.",
    )

    with pytest.raises(
        ValueError,
        match=(
            "items must not contain "
            "conflicting knowledge versions"
        ),
    ):
        KnowledgeGap(
            gap_type=(
                KnowledgeGapType
                .UNRESOLVED_CONTRADICTION
            ),
            items=(first, second),
            applicability=(
                "liquid markets",
            ),
            reason="Conflict is unresolved.",
            snapshot_fingerprint=(
                SNAPSHOT_FINGERPRINT
            ),
        )


@pytest.mark.parametrize(
    ("gap_type", "items", "expected_count"),
    (
        (
            KnowledgeGapType.ISOLATED_ITEM,
            (
                build_item("knowledge-a"),
                build_item("knowledge-b"),
            ),
            1,
        ),
        (
            KnowledgeGapType.UNSUPPORTED_ITEM,
            (
                build_item("knowledge-a"),
                build_item("knowledge-b"),
            ),
            1,
        ),
        (
            (
                KnowledgeGapType
                .UNRESOLVED_CONTRADICTION
            ),
            (build_item("knowledge-a"),),
            2,
        ),
    ),
)
def test_enforces_gap_item_count(
    gap_type: KnowledgeGapType,
    items: tuple[KnowledgeItem, ...],
    expected_count: int,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            f"{gap_type.value} gap must "
            f"reference exactly {expected_count} "
            "KnowledgeItem"
        ),
    ):
        KnowledgeGap(
            gap_type=gap_type,
            items=items,
            applicability=(
                "liquid markets",
            ),
            reason="Detected graph gap.",
            snapshot_fingerprint=(
                SNAPSHOT_FINGERPRINT
            ),
        )


def test_unresolved_gap_requires_different_ids(
) -> None:
    item_v1 = build_item(
        "knowledge-a",
        version=1,
    )
    item_v2 = build_item(
        "knowledge-a",
        version=2,
    )

    with pytest.raises(
        ValueError,
        match=(
            "unresolved_contradiction gap "
            "must reference different "
            "knowledge IDs"
        ),
    ):
        KnowledgeGap(
            gap_type=(
                KnowledgeGapType
                .UNRESOLVED_CONTRADICTION
            ),
            items=(item_v1, item_v2),
            applicability=(
                "liquid markets",
            ),
            reason="Conflict is unresolved.",
            snapshot_fingerprint=(
                SNAPSHOT_FINGERPRINT
            ),
        )


@pytest.mark.parametrize(
    "applicability",
    (
        [],
        set(),
        None,
    ),
)
def test_rejects_non_tuple_applicability(
    applicability: object,
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "applicability must be a tuple"
        ),
    ):
        KnowledgeGap(
            gap_type=(
                KnowledgeGapType.ISOLATED_ITEM
            ),
            items=(build_item("knowledge-a"),),
            applicability=applicability,  # type: ignore[arg-type]
            reason="No graph relations.",
            snapshot_fingerprint=(
                SNAPSHOT_FINGERPRINT
            ),
        )


def test_rejects_empty_applicability(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "applicability must not be empty"
        ),
    ):
        KnowledgeGap(
            gap_type=(
                KnowledgeGapType.ISOLATED_ITEM
            ),
            items=(build_item("knowledge-a"),),
            applicability=(),
            reason="No graph relations.",
            snapshot_fingerprint=(
                SNAPSHOT_FINGERPRINT
            ),
        )


def test_rejects_non_string_applicability_term(
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "each applicability term "
            "must be a string"
        ),
    ):
        KnowledgeGap(
            gap_type=(
                KnowledgeGapType.ISOLATED_ITEM
            ),
            items=(build_item("knowledge-a"),),
            applicability=(
                1,  # type: ignore[arg-type]
            ),
            reason="No graph relations.",
            snapshot_fingerprint=(
                SNAPSHOT_FINGERPRINT
            ),
        )


@pytest.mark.parametrize(
    "term",
    (
        "",
        " ",
        "\t",
    ),
)
def test_rejects_empty_applicability_term(
    term: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "applicability must not "
            "contain empty terms"
        ),
    ):
        KnowledgeGap(
            gap_type=(
                KnowledgeGapType.ISOLATED_ITEM
            ),
            items=(build_item("knowledge-a"),),
            applicability=(term,),
            reason="No graph relations.",
            snapshot_fingerprint=(
                SNAPSHOT_FINGERPRINT
            ),
        )


def test_rejects_duplicate_applicability(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "applicability must not contain "
            "duplicates"
        ),
    ):
        KnowledgeGap(
            gap_type=(
                KnowledgeGapType.ISOLATED_ITEM
            ),
            items=(build_item("knowledge-a"),),
            applicability=(
                "Liquid Markets",
                " liquid markets ",
            ),
            reason="No graph relations.",
            snapshot_fingerprint=(
                SNAPSHOT_FINGERPRINT
            ),
        )


@pytest.mark.parametrize(
    "reason",
    (
        None,
        1,
    ),
)
def test_rejects_non_string_reason(
    reason: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="reason must be a string",
    ):
        KnowledgeGap(
            gap_type=(
                KnowledgeGapType.ISOLATED_ITEM
            ),
            items=(build_item("knowledge-a"),),
            applicability=(
                "liquid markets",
            ),
            reason=reason,  # type: ignore[arg-type]
            snapshot_fingerprint=(
                SNAPSHOT_FINGERPRINT
            ),
        )


@pytest.mark.parametrize(
    "reason",
    (
        "",
        " ",
        "\t",
    ),
)
def test_rejects_empty_reason(
    reason: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="reason must not be empty",
    ):
        KnowledgeGap(
            gap_type=(
                KnowledgeGapType.ISOLATED_ITEM
            ),
            items=(build_item("knowledge-a"),),
            applicability=(
                "liquid markets",
            ),
            reason=reason,
            snapshot_fingerprint=(
                SNAPSHOT_FINGERPRINT
            ),
        )


@pytest.mark.parametrize(
    "snapshot_fingerprint",
    (
        None,
        1,
    ),
)
def test_rejects_non_string_snapshot_fingerprint(
    snapshot_fingerprint: object,
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "snapshot_fingerprint must be "
            "a string"
        ),
    ):
        KnowledgeGap(
            gap_type=(
                KnowledgeGapType.ISOLATED_ITEM
            ),
            items=(build_item("knowledge-a"),),
            applicability=(
                "liquid markets",
            ),
            reason="No graph relations.",
            snapshot_fingerprint=(  # type: ignore[arg-type]
                snapshot_fingerprint
            ),
        )


@pytest.mark.parametrize(
    "snapshot_fingerprint",
    (
        "",
        "a" * 63,
        "a" * 65,
        "g" * 64,
    ),
)
def test_rejects_invalid_snapshot_fingerprint(
    snapshot_fingerprint: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "snapshot_fingerprint must be a "
            "SHA256 hexadecimal digest"
        ),
    ):
        KnowledgeGap(
            gap_type=(
                KnowledgeGapType.ISOLATED_ITEM
            ),
            items=(build_item("knowledge-a"),),
            applicability=(
                "liquid markets",
            ),
            reason="No graph relations.",
            snapshot_fingerprint=(
                snapshot_fingerprint
            ),
        )
