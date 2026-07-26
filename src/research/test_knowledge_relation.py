from dataclasses import FrozenInstanceError

import pytest

from src.research.knowledge_item import KnowledgeItem
from src.research.knowledge_relation import (
    KnowledgeRelation,
    KnowledgeRelationType,
)


def build_item(
    *,
    item_id: str,
    statement: str,
    version: int = 1,
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
        version=version,
        provenance=(
            ("source", f"{item_id}-source"),
        ),
    )


def test_exposes_architectural_relation_types(
) -> None:
    assert tuple(
        relation_type.value
        for relation_type in KnowledgeRelationType
    ) == (
        "supports",
        "contradicts",
        "extends",
        "refines",
        "supersedes",
        "derived_from",
    )


def test_normalizes_reason_and_preserves_direction(
) -> None:
    source = build_item(
        item_id="knowledge-a",
        statement="Momentum persists.",
    )
    target = build_item(
        item_id="knowledge-b",
        statement="Trend evidence is robust.",
    )

    relation = KnowledgeRelation(
        source=source,
        target=target,
        relation_type=KnowledgeRelationType.SUPPORTS,
        reason="  Consistent evidence.  ",
    )

    assert relation.source is source
    assert relation.target is target
    assert (
        relation.relation_type
        is KnowledgeRelationType.SUPPORTS
    )
    assert relation.reason == "Consistent evidence."


def test_canonicalizes_contradicts_endpoints(
) -> None:
    item_b = build_item(
        item_id="knowledge-b",
        statement="Momentum does not persist.",
    )
    item_a = build_item(
        item_id="knowledge-a",
        statement="Momentum persists.",
    )

    relation = KnowledgeRelation(
        source=item_b,
        target=item_a,
        relation_type=(
            KnowledgeRelationType.CONTRADICTS
        ),
        reason="Opposing conclusions.",
    )

    assert relation.source is item_a
    assert relation.target is item_b


def test_contradicts_is_independent_of_endpoint_order(
) -> None:
    item_a = build_item(
        item_id="knowledge-a",
        statement="Momentum persists.",
    )
    item_b = build_item(
        item_id="knowledge-b",
        statement="Momentum does not persist.",
    )

    first = KnowledgeRelation(
        source=item_a,
        target=item_b,
        relation_type=(
            KnowledgeRelationType.CONTRADICTS
        ),
        reason="Opposing conclusions.",
    )
    second = KnowledgeRelation(
        source=item_b,
        target=item_a,
        relation_type=(
            KnowledgeRelationType.CONTRADICTS
        ),
        reason="Opposing conclusions.",
    )

    assert first == second
    assert first.fingerprint == second.fingerprint


def test_directed_relation_depends_on_endpoint_order(
) -> None:
    item_a = build_item(
        item_id="knowledge-a",
        statement="Statement A.",
    )
    item_b = build_item(
        item_id="knowledge-b",
        statement="Statement B.",
    )

    forward = KnowledgeRelation(
        source=item_a,
        target=item_b,
        relation_type=KnowledgeRelationType.EXTENDS,
        reason="Adds a regime condition.",
    )
    reverse = KnowledgeRelation(
        source=item_b,
        target=item_a,
        relation_type=KnowledgeRelationType.EXTENDS,
        reason="Adds a regime condition.",
    )

    assert forward != reverse
    assert forward.fingerprint != reverse.fingerprint


def test_serializes_exact_versioned_references(
) -> None:
    source = build_item(
        item_id="knowledge-a",
        statement="Updated statement A.",
        version=2,
    )
    target = build_item(
        item_id="knowledge-b",
        statement="Statement B.",
        version=3,
    )
    relation = KnowledgeRelation(
        source=source,
        target=target,
        relation_type=KnowledgeRelationType.REFINES,
        reason="Narrows applicability.",
    )

    assert relation.to_dict() == {
        "schema_version": 1,
        "source": {
            "id": "knowledge-a",
            "version": 2,
            "fingerprint": source.fingerprint,
        },
        "target": {
            "id": "knowledge-b",
            "version": 3,
            "fingerprint": target.fingerprint,
        },
        "relation_type": "refines",
        "reason": "Narrows applicability.",
    }


def test_fingerprint_changes_with_relation_type(
) -> None:
    source = build_item(
        item_id="knowledge-a",
        statement="Statement A.",
    )
    target = build_item(
        item_id="knowledge-b",
        statement="Statement B.",
    )

    supports = KnowledgeRelation(
        source=source,
        target=target,
        relation_type=KnowledgeRelationType.SUPPORTS,
        reason="Shared evidence.",
    )
    extends = KnowledgeRelation(
        source=source,
        target=target,
        relation_type=KnowledgeRelationType.EXTENDS,
        reason="Shared evidence.",
    )

    assert supports.fingerprint != extends.fingerprint
    assert len(supports.fingerprint) == 64


def test_fingerprint_changes_with_reason(
) -> None:
    source = build_item(
        item_id="knowledge-a",
        statement="Statement A.",
    )
    target = build_item(
        item_id="knowledge-b",
        statement="Statement B.",
    )

    first = KnowledgeRelation(
        source=source,
        target=target,
        relation_type=KnowledgeRelationType.SUPPORTS,
        reason="Shared evidence.",
    )
    second = KnowledgeRelation(
        source=source,
        target=target,
        relation_type=KnowledgeRelationType.SUPPORTS,
        reason="Independent confirmation.",
    )

    assert first.fingerprint != second.fingerprint


def test_fingerprint_changes_with_item_version(
) -> None:
    source_v1 = build_item(
        item_id="knowledge-a",
        statement="Statement A.",
        version=1,
    )
    source_v2 = build_item(
        item_id="knowledge-a",
        statement="Updated statement A.",
        version=2,
    )
    target = build_item(
        item_id="knowledge-b",
        statement="Statement B.",
    )

    first = KnowledgeRelation(
        source=source_v1,
        target=target,
        relation_type=KnowledgeRelationType.SUPPORTS,
        reason="Shared evidence.",
    )
    second = KnowledgeRelation(
        source=source_v2,
        target=target,
        relation_type=KnowledgeRelationType.SUPPORTS,
        reason="Shared evidence.",
    )

    assert first.fingerprint != second.fingerprint


def test_is_immutable() -> None:
    relation = KnowledgeRelation(
        source=build_item(
            item_id="knowledge-a",
            statement="Statement A.",
        ),
        target=build_item(
            item_id="knowledge-b",
            statement="Statement B.",
        ),
        relation_type=KnowledgeRelationType.SUPPORTS,
        reason="Shared evidence.",
    )

    with pytest.raises(FrozenInstanceError):
        relation.reason = "Changed"  # type: ignore[misc]


@pytest.mark.parametrize(
    ("field_name", "source", "target"),
    (
        (
            "source",
            object(),
            build_item(
                item_id="knowledge-b",
                statement="Statement B.",
            ),
        ),
        (
            "target",
            build_item(
                item_id="knowledge-a",
                statement="Statement A.",
            ),
            object(),
        ),
    ),
)
def test_rejects_non_knowledge_item_endpoint(
    field_name: str,
    source: object,
    target: object,
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            f"{field_name} must be a KnowledgeItem"
        ),
    ):
        KnowledgeRelation(
            source=source,  # type: ignore[arg-type]
            target=target,  # type: ignore[arg-type]
            relation_type=(
                KnowledgeRelationType.SUPPORTS
            ),
            reason="Shared evidence.",
        )


@pytest.mark.parametrize(
    "relation_type",
    (
        "supports",
        None,
        1,
    ),
)
def test_rejects_non_relation_type(
    relation_type: object,
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "relation_type must be a "
            "KnowledgeRelationType"
        ),
    ):
        KnowledgeRelation(
            source=build_item(
                item_id="knowledge-a",
                statement="Statement A.",
            ),
            target=build_item(
                item_id="knowledge-b",
                statement="Statement B.",
            ),
            relation_type=relation_type,  # type: ignore[arg-type]
            reason="Shared evidence.",
        )


def test_rejects_same_item_version() -> None:
    item = build_item(
        item_id="knowledge-a",
        statement="Statement A.",
    )

    with pytest.raises(
        ValueError,
        match=(
            "source and target must reference "
            "different knowledge versions"
        ),
    ):
        KnowledgeRelation(
            source=item,
            target=item,
            relation_type=(
                KnowledgeRelationType.SUPPORTS
            ),
            reason="Self reference.",
        )


def test_rejects_conflicting_same_id_and_version(
) -> None:
    first = build_item(
        item_id="knowledge-a",
        statement="Statement A.",
        version=1,
    )
    second = build_item(
        item_id="knowledge-a",
        statement="Conflicting statement A.",
        version=1,
    )

    with pytest.raises(
        ValueError,
        match=(
            "source and target must reference "
            "different knowledge versions"
        ),
    ):
        KnowledgeRelation(
            source=first,
            target=second,
            relation_type=(
                KnowledgeRelationType.SUPPORTS
            ),
            reason="Invalid version reference.",
        )


def test_allows_relation_between_versions_of_same_id(
) -> None:
    older = build_item(
        item_id="knowledge-a",
        statement="Statement A.",
        version=1,
    )
    newer = build_item(
        item_id="knowledge-a",
        statement="Updated statement A.",
        version=2,
    )

    relation = KnowledgeRelation(
        source=newer,
        target=older,
        relation_type=(
            KnowledgeRelationType.SUPERSEDES
        ),
        reason="Updated evidence.",
    )

    assert relation.source is newer
    assert relation.target is older


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
        KnowledgeRelation(
            source=build_item(
                item_id="knowledge-a",
                statement="Statement A.",
            ),
            target=build_item(
                item_id="knowledge-b",
                statement="Statement B.",
            ),
            relation_type=(
                KnowledgeRelationType.SUPPORTS
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
        KnowledgeRelation(
            source=build_item(
                item_id="knowledge-a",
                statement="Statement A.",
            ),
            target=build_item(
                item_id="knowledge-b",
                statement="Statement B.",
            ),
            relation_type=(
                KnowledgeRelationType.SUPPORTS
            ),
            reason=reason,
        )
