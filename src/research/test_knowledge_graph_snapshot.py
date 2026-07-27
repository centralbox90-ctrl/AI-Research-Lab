import json
from dataclasses import FrozenInstanceError

import pytest

from src.research.knowledge_graph import KnowledgeGraph
from src.research.knowledge_graph_snapshot import (
    KnowledgeGraphSnapshot,
)
from src.research.knowledge_item import KnowledgeItem
from src.research.knowledge_relation import (
    KnowledgeRelation,
    KnowledgeRelationType,
)


class RelationRepositoryStub:
    def __init__(
        self,
        relations: tuple[
            KnowledgeRelation,
            ...,
        ] = (),
    ) -> None:
        self._relations = relations

    def save(
        self,
        relation: KnowledgeRelation,
    ) -> None:
        raise NotImplementedError

    def list_all(
        self,
    ) -> tuple[KnowledgeRelation, ...]:
        return self._relations

    def outgoing(
        self,
        item_id: str,
        *,
        version: int | None = None,
        relation_type: (
            KnowledgeRelationType | None
        ) = None,
    ) -> tuple[KnowledgeRelation, ...]:
        raise NotImplementedError

    def incoming(
        self,
        item_id: str,
        *,
        version: int | None = None,
        relation_type: (
            KnowledgeRelationType | None
        ) = None,
    ) -> tuple[KnowledgeRelation, ...]:
        raise NotImplementedError

    def relations_for(
        self,
        item_id: str,
        *,
        version: int | None = None,
        relation_type: (
            KnowledgeRelationType | None
        ) = None,
    ) -> tuple[KnowledgeRelation, ...]:
        raise NotImplementedError


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


def build_relation(
    source: KnowledgeItem,
    target: KnowledgeItem,
    *,
    relation_type: KnowledgeRelationType = (
        KnowledgeRelationType.SUPPORTS
    ),
    reason: str = "Shared evidence.",
) -> KnowledgeRelation:
    return KnowledgeRelation(
        source=source,
        target=target,
        relation_type=relation_type,
        reason=reason,
    )


def build_graph(
    *relations: KnowledgeRelation,
) -> KnowledgeGraph:
    return KnowledgeGraph(
        RelationRepositoryStub(
            tuple(relations)
        )
    )


def test_allows_empty_snapshot() -> None:
    snapshot = KnowledgeGraphSnapshot(
        items=(),
        relations=(),
    )

    assert snapshot.items == ()
    assert snapshot.relations == ()
    assert snapshot.to_dict() == {
        "schema_version": 1,
        "items": [],
        "relations": [],
    }


def test_canonicalizes_items_and_relations(
) -> None:
    item_a = build_item("knowledge-a")
    item_b = build_item("knowledge-b")
    item_c = build_item("knowledge-c")
    relation_ab = build_relation(
        item_a,
        item_b,
    )
    relation_bc = build_relation(
        item_b,
        item_c,
    )

    snapshot = KnowledgeGraphSnapshot(
        items=(item_c, item_b, item_a),
        relations=(
            relation_bc,
            relation_ab,
        ),
    )

    assert snapshot.items == (
        item_a,
        item_b,
        item_c,
    )
    assert snapshot.relations == (
        relation_ab,
        relation_bc,
    )


def test_serializes_schema_items_and_relations(
) -> None:
    item_a = build_item("knowledge-a")
    item_b = build_item("knowledge-b")
    relation = build_relation(
        item_a,
        item_b,
    )
    snapshot = KnowledgeGraphSnapshot(
        items=(item_a, item_b),
        relations=(relation,),
    )

    payload = snapshot.to_dict()

    assert payload["schema_version"] == 1
    assert payload["items"] == [
        {
            **item_a.to_dict(),
            "fingerprint": (
                item_a.fingerprint
            ),
        },
        {
            **item_b.to_dict(),
            "fingerprint": (
                item_b.fingerprint
            ),
        },
    ]
    assert payload["relations"] == [
        relation.to_dict()
    ]


def test_json_is_compact_and_round_trips(
) -> None:
    item_a = build_item("knowledge-a")
    item_b = build_item("knowledge-b")
    snapshot = KnowledgeGraphSnapshot(
        items=(item_a, item_b),
        relations=(
            build_relation(
                item_a,
                item_b,
            ),
        ),
    )

    serialized = snapshot.to_json()

    assert json.loads(serialized) == (
        snapshot.to_dict()
    )
    assert "\n" not in serialized
    assert ": " not in serialized


def test_fingerprint_is_deterministic_for_input_order(
) -> None:
    item_a = build_item("knowledge-a")
    item_b = build_item("knowledge-b")
    item_c = build_item("knowledge-c")
    relation_ab = build_relation(
        item_a,
        item_b,
    )
    relation_bc = build_relation(
        item_b,
        item_c,
    )

    first = KnowledgeGraphSnapshot(
        items=(item_a, item_b, item_c),
        relations=(
            relation_ab,
            relation_bc,
        ),
    )
    second = KnowledgeGraphSnapshot(
        items=(item_c, item_a, item_b),
        relations=(
            relation_bc,
            relation_ab,
        ),
    )

    assert first.to_json() == second.to_json()
    assert first.fingerprint == (
        second.fingerprint
    )
    assert len(first.fingerprint) == 64


def test_fingerprint_changes_with_relation(
) -> None:
    item_a = build_item("knowledge-a")
    item_b = build_item("knowledge-b")

    first = KnowledgeGraphSnapshot(
        items=(item_a, item_b),
        relations=(
            build_relation(
                item_a,
                item_b,
            ),
        ),
    )
    second = KnowledgeGraphSnapshot(
        items=(item_a, item_b),
        relations=(
            build_relation(
                item_a,
                item_b,
                reason="Different evidence.",
            ),
        ),
    )

    assert first.fingerprint != (
        second.fingerprint
    )


def test_builds_snapshot_from_graph() -> None:
    item_a = build_item("knowledge-a")
    item_b = build_item("knowledge-b")
    item_c = build_item("knowledge-c")
    relation_bc = build_relation(
        item_b,
        item_c,
    )
    relation_ab = build_relation(
        item_a,
        item_b,
    )

    snapshot = (
        KnowledgeGraphSnapshot.from_graph(
            build_graph(
                relation_bc,
                relation_ab,
            )
        )
    )

    assert snapshot.items == (
        item_a,
        item_b,
        item_c,
    )
    assert snapshot.relations == (
        relation_ab,
        relation_bc,
    )


def test_builds_empty_snapshot_from_graph(
) -> None:
    snapshot = (
        KnowledgeGraphSnapshot.from_graph(
            build_graph()
        )
    )

    assert snapshot == KnowledgeGraphSnapshot(
        items=(),
        relations=(),
    )


def test_snapshot_is_immutable() -> None:
    snapshot = KnowledgeGraphSnapshot(
        items=(),
        relations=(),
    )

    with pytest.raises(FrozenInstanceError):
        snapshot.items = ()  # type: ignore[misc]


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
        KnowledgeGraphSnapshot(
            items=items,  # type: ignore[arg-type]
            relations=(),
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
        KnowledgeGraphSnapshot(
            items=(
                object(),  # type: ignore[arg-type]
            ),
            relations=(),
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
        KnowledgeGraphSnapshot(
            items=(item, item),
            relations=(),
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
        KnowledgeGraphSnapshot(
            items=(first, second),
            relations=(),
        )


@pytest.mark.parametrize(
    "relations",
    (
        [],
        set(),
        None,
    ),
)
def test_rejects_non_tuple_relations(
    relations: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="relations must be a tuple",
    ):
        KnowledgeGraphSnapshot(
            items=(),
            relations=relations,  # type: ignore[arg-type]
        )


def test_rejects_non_knowledge_relation(
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "each relation must be a "
            "KnowledgeRelation"
        ),
    ):
        KnowledgeGraphSnapshot(
            items=(),
            relations=(
                object(),  # type: ignore[arg-type]
            ),
        )


def test_rejects_duplicate_relation_fingerprint(
) -> None:
    item_a = build_item("knowledge-a")
    item_b = build_item("knowledge-b")
    relation = build_relation(
        item_a,
        item_b,
    )

    with pytest.raises(
        ValueError,
        match=(
            "relations must not contain "
            "duplicate fingerprints"
        ),
    ):
        KnowledgeGraphSnapshot(
            items=(item_a, item_b),
            relations=(
                relation,
                relation,
            ),
        )


@pytest.mark.parametrize(
    "included_endpoint",
    (
        "source",
        "target",
    ),
)
def test_requires_each_relation_endpoint(
    included_endpoint: str,
) -> None:
    item_a = build_item("knowledge-a")
    item_b = build_item("knowledge-b")
    relation = build_relation(
        item_a,
        item_b,
    )
    included_item = (
        item_a
        if included_endpoint == "source"
        else item_b
    )

    with pytest.raises(
        ValueError,
        match=(
            "relation endpoints must "
            "reference snapshot items"
        ),
    ):
        KnowledgeGraphSnapshot(
            items=(included_item,),
            relations=(relation,),
        )


def test_requires_knowledge_graph() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "graph must be a KnowledgeGraph"
        ),
    ):
        KnowledgeGraphSnapshot.from_graph(
            object(),  # type: ignore[arg-type]
        )
