import pytest

from src.research.knowledge_gap import (
    KnowledgeGap,
    KnowledgeGapType,
)
from src.research.knowledge_gap_detector import (
    KnowledgeGapDetector,
)
from src.research.knowledge_graph_snapshot import (
    KnowledgeGraphSnapshot,
)
from src.research.knowledge_item import KnowledgeItem
from src.research.knowledge_relation import (
    KnowledgeRelation,
    KnowledgeRelationType,
)


def build_item(
    item_id: str,
    *,
    version: int = 1,
    statement: str | None = None,
    applicability: tuple[str, ...] = (
        "liquid markets",
    ),
) -> KnowledgeItem:
    return KnowledgeItem(
        id=item_id,
        statement=(
            statement
            or f"Statement {item_id}."
        ),
        confidence=0.85,
        applicability=applicability,
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


def build_relation(
    source: KnowledgeItem,
    target: KnowledgeItem,
    *,
    relation_type: KnowledgeRelationType,
    reason: str = "Explicit graph relation.",
) -> KnowledgeRelation:
    return KnowledgeRelation(
        source=source,
        target=target,
        relation_type=relation_type,
        reason=reason,
    )


def build_snapshot(
    *,
    items: tuple[KnowledgeItem, ...],
    relations: tuple[
        KnowledgeRelation,
        ...,
    ] = (),
) -> KnowledgeGraphSnapshot:
    return KnowledgeGraphSnapshot(
        items=items,
        relations=relations,
    )


def gaps_of_type(
    gaps: tuple[KnowledgeGap, ...],
    gap_type: KnowledgeGapType,
) -> tuple[KnowledgeGap, ...]:
    return tuple(
        gap
        for gap in gaps
        if gap.gap_type is gap_type
    )


def test_requires_graph_snapshot() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "snapshot must be a "
            "KnowledgeGraphSnapshot"
        ),
    ):
        KnowledgeGapDetector().detect(
            object(),  # type: ignore[arg-type]
        )


def test_empty_snapshot_has_no_gaps(
) -> None:
    snapshot = build_snapshot(items=())

    assert (
        KnowledgeGapDetector().detect(
            snapshot
        )
        == ()
    )


def test_detects_isolated_item() -> None:
    item = build_item("knowledge-a")
    snapshot = build_snapshot(
        items=(item,),
    )

    gaps = KnowledgeGapDetector().detect(
        snapshot
    )

    assert len(gaps) == 1
    assert gaps[0].gap_type is (
        KnowledgeGapType.ISOLATED_ITEM
    )
    assert gaps[0].items == (item,)
    assert gaps[0].applicability == (
        "liquid markets",
    )
    assert gaps[0].reason == (
        "Knowledge item has no graph "
        "relations."
    )
    assert gaps[0].snapshot_fingerprint == (
        snapshot.fingerprint
    )


def test_detects_connected_unsupported_items(
) -> None:
    item_a = build_item("knowledge-a")
    item_b = build_item("knowledge-b")
    relation = build_relation(
        item_b,
        item_a,
        relation_type=(
            KnowledgeRelationType.EXTENDS
        ),
    )
    snapshot = build_snapshot(
        items=(item_b, item_a),
        relations=(relation,),
    )

    gaps = KnowledgeGapDetector().detect(
        snapshot
    )

    assert tuple(
        gap.items[0]
        for gap in gaps
    ) == (
        item_a,
        item_b,
    )
    assert all(
        gap.gap_type
        is KnowledgeGapType.UNSUPPORTED_ITEM
        for gap in gaps
    )


def test_incoming_support_grounds_target(
) -> None:
    source = build_item("knowledge-a")
    target = build_item("knowledge-b")
    relation = build_relation(
        source,
        target,
        relation_type=(
            KnowledgeRelationType.SUPPORTS
        ),
    )
    snapshot = build_snapshot(
        items=(target, source),
        relations=(relation,),
    )

    gaps = KnowledgeGapDetector().detect(
        snapshot
    )

    assert gaps_of_type(
        gaps,
        KnowledgeGapType.UNSUPPORTED_ITEM,
    )[0].items == (source,)
    assert not any(
        target in gap.items
        for gap in gaps
    )


def test_outgoing_derived_from_grounds_source(
) -> None:
    derived = build_item("knowledge-a")
    origin = build_item("knowledge-b")
    relation = build_relation(
        derived,
        origin,
        relation_type=(
            KnowledgeRelationType.DERIVED_FROM
        ),
    )
    snapshot = build_snapshot(
        items=(origin, derived),
        relations=(relation,),
    )

    gaps = KnowledgeGapDetector().detect(
        snapshot
    )

    assert gaps_of_type(
        gaps,
        KnowledgeGapType.UNSUPPORTED_ITEM,
    )[0].items == (origin,)
    assert not any(
        derived in gap.items
        for gap in gaps
    )


def test_historical_support_does_not_ground_item(
) -> None:
    old_source = build_item(
        "knowledge-a",
        version=1,
    )
    new_source = build_item(
        "knowledge-a",
        version=2,
    )
    target = build_item("knowledge-b")
    supersedes = build_relation(
        new_source,
        old_source,
        relation_type=(
            KnowledgeRelationType.SUPERSEDES
        ),
    )
    supports = build_relation(
        old_source,
        target,
        relation_type=(
            KnowledgeRelationType.SUPPORTS
        ),
    )
    snapshot = build_snapshot(
        items=(
            target,
            old_source,
            new_source,
        ),
        relations=(
            supports,
            supersedes,
        ),
    )

    gaps = KnowledgeGapDetector().detect(
        snapshot
    )
    unsupported_items = tuple(
        gap.items[0]
        for gap in gaps_of_type(
            gaps,
            KnowledgeGapType.UNSUPPORTED_ITEM,
        )
    )

    assert unsupported_items == (
        new_source,
        target,
    )
    assert not any(
        old_source in gap.items
        for gap in gaps
    )


def test_detects_unresolved_contradiction(
) -> None:
    item_a = build_item(
        "knowledge-a",
        applicability=(
            "trending markets",
            "liquid markets",
        ),
    )
    item_b = build_item(
        "knowledge-b",
        applicability=(
            "LIQUID MARKETS",
            "volatile markets",
        ),
    )
    relation = build_relation(
        item_b,
        item_a,
        relation_type=(
            KnowledgeRelationType.CONTRADICTS
        ),
        reason="Opposing conclusions.",
    )
    snapshot = build_snapshot(
        items=(item_b, item_a),
        relations=(relation,),
    )

    gaps = gaps_of_type(
        KnowledgeGapDetector().detect(
            snapshot
        ),
        (
            KnowledgeGapType
            .UNRESOLVED_CONTRADICTION
        ),
    )

    assert len(gaps) == 1
    assert gaps[0].items == (
        item_a,
        item_b,
    )
    assert gaps[0].applicability == (
        "liquid markets",
    )
    assert gaps[0].reason == (
        "Contradicting knowledge items "
        "have not been superseded."
    )


def test_skips_non_overlapping_contradiction(
) -> None:
    item_a = build_item(
        "knowledge-a",
        applicability=("spot markets",),
    )
    item_b = build_item(
        "knowledge-b",
        applicability=("futures markets",),
    )
    relation = build_relation(
        item_a,
        item_b,
        relation_type=(
            KnowledgeRelationType.CONTRADICTS
        ),
    )
    snapshot = build_snapshot(
        items=(item_a, item_b),
        relations=(relation,),
    )

    gaps = KnowledgeGapDetector().detect(
        snapshot
    )

    assert gaps_of_type(
        gaps,
        (
            KnowledgeGapType
            .UNRESOLVED_CONTRADICTION
        ),
    ) == ()


@pytest.mark.parametrize(
    "superseded_side",
    (
        "left",
        "right",
    ),
)
def test_superseding_either_side_resolves_contradiction(
    superseded_side: str,
) -> None:
    item_a = build_item("knowledge-a")
    item_b = build_item("knowledge-b")
    old_item = (
        item_a
        if superseded_side == "left"
        else item_b
    )
    new_item = build_item(
        old_item.id,
        version=2,
    )
    contradiction = build_relation(
        item_a,
        item_b,
        relation_type=(
            KnowledgeRelationType.CONTRADICTS
        ),
    )
    supersedes = build_relation(
        new_item,
        old_item,
        relation_type=(
            KnowledgeRelationType.SUPERSEDES
        ),
    )
    snapshot = build_snapshot(
        items=(item_a, item_b, new_item),
        relations=(
            contradiction,
            supersedes,
        ),
    )

    gaps = KnowledgeGapDetector().detect(
        snapshot
    )

    assert gaps_of_type(
        gaps,
        (
            KnowledgeGapType
            .UNRESOLVED_CONTRADICTION
        ),
    ) == ()


def test_deduplicates_equivalent_contradictions(
) -> None:
    item_a = build_item("knowledge-a")
    item_b = build_item("knowledge-b")
    first = build_relation(
        item_a,
        item_b,
        relation_type=(
            KnowledgeRelationType.CONTRADICTS
        ),
        reason="First explicit rule.",
    )
    second = build_relation(
        item_a,
        item_b,
        relation_type=(
            KnowledgeRelationType.CONTRADICTS
        ),
        reason="Second explicit rule.",
    )
    snapshot = build_snapshot(
        items=(item_a, item_b),
        relations=(second, first),
    )

    gaps = gaps_of_type(
        KnowledgeGapDetector().detect(
            snapshot
        ),
        (
            KnowledgeGapType
            .UNRESOLVED_CONTRADICTION
        ),
    )

    assert len(gaps) == 1


def test_orders_gap_types_and_items_deterministically(
) -> None:
    isolated = build_item("knowledge-a")
    unsupported_b = build_item("knowledge-b")
    unsupported_c = build_item("knowledge-c")
    contradiction_d = build_item("knowledge-d")
    contradiction_e = build_item("knowledge-e")
    extends = build_relation(
        unsupported_c,
        unsupported_b,
        relation_type=(
            KnowledgeRelationType.EXTENDS
        ),
    )
    contradicts = build_relation(
        contradiction_e,
        contradiction_d,
        relation_type=(
            KnowledgeRelationType.CONTRADICTS
        ),
    )
    snapshot = build_snapshot(
        items=(
            contradiction_e,
            unsupported_c,
            isolated,
            contradiction_d,
            unsupported_b,
        ),
        relations=(
            contradicts,
            extends,
        ),
    )

    gaps = KnowledgeGapDetector().detect(
        snapshot
    )

    assert tuple(
        gap.gap_type
        for gap in gaps
    ) == (
        KnowledgeGapType.ISOLATED_ITEM,
        KnowledgeGapType.UNSUPPORTED_ITEM,
        KnowledgeGapType.UNSUPPORTED_ITEM,
        KnowledgeGapType.UNSUPPORTED_ITEM,
        KnowledgeGapType.UNSUPPORTED_ITEM,
        (
            KnowledgeGapType
            .UNRESOLVED_CONTRADICTION
        ),
    )
    assert tuple(
        gap.items[0].id
        for gap in gaps[1:5]
    ) == (
        "knowledge-b",
        "knowledge-c",
        "knowledge-d",
        "knowledge-e",
    )


def test_every_gap_references_exact_snapshot(
) -> None:
    isolated = build_item("knowledge-a")
    unsupported_a = build_item("knowledge-b")
    unsupported_b = build_item("knowledge-c")
    relation = build_relation(
        unsupported_a,
        unsupported_b,
        relation_type=(
            KnowledgeRelationType.EXTENDS
        ),
    )
    snapshot = build_snapshot(
        items=(
            unsupported_b,
            isolated,
            unsupported_a,
        ),
        relations=(relation,),
    )

    gaps = KnowledgeGapDetector().detect(
        snapshot
    )

    assert gaps
    assert {
        gap.snapshot_fingerprint
        for gap in gaps
    } == {
        snapshot.fingerprint
    }
