import pytest

from src.research.knowledge_graph import (
    KnowledgeGraph,
    KnowledgeTraversalDirection,
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
        return tuple(
            relation
            for relation in self._relations
            if relation.source.id == item_id
            and (
                version is None
                or relation.source.version
                == version
            )
            and (
                relation_type is None
                or relation.relation_type
                is relation_type
            )
        )

    def incoming(
        self,
        item_id: str,
        *,
        version: int | None = None,
        relation_type: (
            KnowledgeRelationType | None
        ) = None,
    ) -> tuple[KnowledgeRelation, ...]:
        return tuple(
            relation
            for relation in self._relations
            if relation.target.id == item_id
            and (
                version is None
                or relation.target.version
                == version
            )
            and (
                relation_type is None
                or relation.relation_type
                is relation_type
            )
        )

    def relations_for(
        self,
        item_id: str,
        *,
        version: int | None = None,
        relation_type: (
            KnowledgeRelationType | None
        ) = None,
    ) -> tuple[KnowledgeRelation, ...]:
        return tuple(
            relation
            for relation in self._relations
            if (
                (
                    relation.source.id
                    == item_id
                    and (
                        version is None
                        or relation.source.version
                        == version
                    )
                )
                or (
                    relation.target.id
                    == item_id
                    and (
                        version is None
                        or relation.target.version
                        == version
                    )
                )
            )
            and (
                relation_type is None
                or relation.relation_type
                is relation_type
            )
        )


def build_item(
    item_id: str,
    *,
    version: int = 1,
) -> KnowledgeItem:
    return KnowledgeItem(
        id=item_id,
        statement=f"Statement {item_id}.",
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


def test_exposes_traversal_directions() -> None:
    assert tuple(
        direction.value
        for direction
        in KnowledgeTraversalDirection
    ) == (
        "outgoing",
        "incoming",
        "both",
    )


def test_requires_relation_repository() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "repository must implement "
            "KnowledgeRelationRepository"
        ),
    ):
        KnowledgeGraph(
            object(),  # type: ignore[arg-type]
        )


def test_returns_relations_in_repository_order(
) -> None:
    item_a = build_item("knowledge-a")
    item_b = build_item("knowledge-b")
    item_c = build_item("knowledge-c")
    second = build_relation(
        item_b,
        item_c,
    )
    first = build_relation(
        item_a,
        item_b,
    )
    graph = build_graph(second, first)

    assert graph.relations() == (
        second,
        first,
    )


def test_outgoing_neighbors_are_deterministic(
) -> None:
    item_a = build_item("knowledge-a")
    item_b = build_item("knowledge-b")
    item_c = build_item("knowledge-c")
    graph = build_graph(
        build_relation(item_a, item_c),
        build_relation(item_a, item_b),
    )

    assert graph.neighbors(
        item_a,
        direction=(
            KnowledgeTraversalDirection.OUTGOING
        ),
    ) == (
        item_b,
        item_c,
    )


def test_incoming_neighbors_are_deterministic(
) -> None:
    item_a = build_item("knowledge-a")
    item_b = build_item("knowledge-b")
    item_c = build_item("knowledge-c")
    graph = build_graph(
        build_relation(item_c, item_b),
        build_relation(item_a, item_b),
    )

    assert graph.neighbors(
        item_b,
        direction=(
            KnowledgeTraversalDirection.INCOMING
        ),
    ) == (
        item_a,
        item_c,
    )


def test_both_neighbors_include_each_direction(
) -> None:
    item_a = build_item("knowledge-a")
    item_b = build_item("knowledge-b")
    item_c = build_item("knowledge-c")
    graph = build_graph(
        build_relation(item_a, item_b),
        build_relation(item_c, item_a),
    )

    assert graph.neighbors(item_a) == (
        item_b,
        item_c,
    )


def test_neighbors_require_exact_item_version(
) -> None:
    item_a_v1 = build_item(
        "knowledge-a",
        version=1,
    )
    item_a_v2 = build_item(
        "knowledge-a",
        version=2,
    )
    item_b = build_item("knowledge-b")
    graph = build_graph(
        build_relation(item_a_v1, item_b)
    )

    assert graph.neighbors(
        item_a_v2,
        direction=(
            KnowledgeTraversalDirection.OUTGOING
        ),
    ) == ()


def test_neighbors_deduplicate_same_item(
) -> None:
    item_a = build_item("knowledge-a")
    item_b = build_item("knowledge-b")
    graph = build_graph(
        build_relation(item_a, item_b),
        build_relation(
            item_a,
            item_b,
            relation_type=(
                KnowledgeRelationType.EXTENDS
            ),
            reason="Adds a regime condition.",
        ),
    )

    assert graph.neighbors(
        item_a,
        direction=(
            KnowledgeTraversalDirection.OUTGOING
        ),
    ) == (item_b,)


def test_neighbors_filter_relation_types(
) -> None:
    item_a = build_item("knowledge-a")
    item_b = build_item("knowledge-b")
    item_c = build_item("knowledge-c")
    graph = build_graph(
        build_relation(item_a, item_b),
        build_relation(
            item_a,
            item_c,
            relation_type=(
                KnowledgeRelationType.EXTENDS
            ),
            reason="Adds a regime condition.",
        ),
    )

    assert graph.neighbors(
        item_a,
        direction=(
            KnowledgeTraversalDirection.OUTGOING
        ),
        relation_types=(
            KnowledgeRelationType.SUPPORTS,
        ),
    ) == (item_b,)


def test_empty_relation_types_matches_nothing(
) -> None:
    item_a = build_item("knowledge-a")
    item_b = build_item("knowledge-b")
    graph = build_graph(
        build_relation(item_a, item_b)
    )

    assert graph.neighbors(
        item_a,
        relation_types=(),
    ) == ()


def test_zero_depth_returns_empty() -> None:
    item_a = build_item("knowledge-a")
    item_b = build_item("knowledge-b")
    graph = build_graph(
        build_relation(item_a, item_b)
    )

    assert graph.traverse(
        item_a,
        max_depth=0,
    ) == ()


def test_one_depth_returns_direct_neighbors(
) -> None:
    item_a = build_item("knowledge-a")
    item_b = build_item("knowledge-b")
    item_c = build_item("knowledge-c")
    graph = build_graph(
        build_relation(item_a, item_c),
        build_relation(item_a, item_b),
        build_relation(item_b, item_c),
    )

    assert graph.traverse(
        item_a,
        max_depth=1,
    ) == (
        item_b,
        item_c,
    )


def test_traversal_is_breadth_first_and_deterministic(
) -> None:
    item_a = build_item("knowledge-a")
    item_b = build_item("knowledge-b")
    item_c = build_item("knowledge-c")
    item_d = build_item("knowledge-d")
    item_e = build_item("knowledge-e")
    graph = build_graph(
        build_relation(item_c, item_e),
        build_relation(item_a, item_c),
        build_relation(item_b, item_d),
        build_relation(item_a, item_b),
    )

    assert graph.traverse(
        item_a,
        max_depth=2,
    ) == (
        item_b,
        item_c,
        item_d,
        item_e,
    )


def test_traversal_stops_on_cycle() -> None:
    item_a = build_item("knowledge-a")
    item_b = build_item("knowledge-b")
    item_c = build_item("knowledge-c")
    graph = build_graph(
        build_relation(item_a, item_b),
        build_relation(item_b, item_c),
        build_relation(item_c, item_a),
    )

    assert graph.traverse(
        item_a,
        max_depth=10,
    ) == (
        item_b,
        item_c,
    )


def test_traversal_deduplicates_converging_paths(
) -> None:
    item_a = build_item("knowledge-a")
    item_b = build_item("knowledge-b")
    item_c = build_item("knowledge-c")
    item_d = build_item("knowledge-d")
    graph = build_graph(
        build_relation(item_a, item_b),
        build_relation(item_a, item_c),
        build_relation(item_b, item_d),
        build_relation(item_c, item_d),
    )

    assert graph.traverse(
        item_a,
        max_depth=2,
    ) == (
        item_b,
        item_c,
        item_d,
    )


def test_traverses_incoming_relations() -> None:
    item_a = build_item("knowledge-a")
    item_b = build_item("knowledge-b")
    item_c = build_item("knowledge-c")
    graph = build_graph(
        build_relation(item_a, item_b),
        build_relation(item_b, item_c),
    )

    assert graph.traverse(
        item_c,
        max_depth=2,
        direction=(
            KnowledgeTraversalDirection.INCOMING
        ),
    ) == (
        item_b,
        item_a,
    )


def test_traverses_both_directions() -> None:
    item_a = build_item("knowledge-a")
    item_b = build_item("knowledge-b")
    item_c = build_item("knowledge-c")
    graph = build_graph(
        build_relation(item_a, item_b),
        build_relation(item_c, item_a),
    )

    assert graph.traverse(
        item_a,
        max_depth=1,
        direction=(
            KnowledgeTraversalDirection.BOTH
        ),
    ) == (
        item_b,
        item_c,
    )


def test_traversal_filters_relation_types(
) -> None:
    item_a = build_item("knowledge-a")
    item_b = build_item("knowledge-b")
    item_c = build_item("knowledge-c")
    graph = build_graph(
        build_relation(item_a, item_b),
        build_relation(
            item_a,
            item_c,
            relation_type=(
                KnowledgeRelationType.EXTENDS
            ),
            reason="Adds a regime condition.",
        ),
    )

    assert graph.traverse(
        item_a,
        max_depth=1,
        relation_types=(
            KnowledgeRelationType.SUPPORTS,
        ),
    ) == (item_b,)


@pytest.mark.parametrize(
    "method_name",
    (
        "neighbors",
        "traverse",
    ),
)
def test_rejects_non_knowledge_item(
    method_name: str,
) -> None:
    graph = build_graph()
    method = getattr(graph, method_name)

    with pytest.raises(
        TypeError,
        match="item must be a KnowledgeItem",
    ):
        if method_name == "traverse":
            method(
                object(),
                max_depth=1,
            )
        else:
            method(object())


@pytest.mark.parametrize(
    ("method_name", "direction"),
    (
        ("neighbors", "outgoing"),
        ("neighbors", None),
        ("traverse", "outgoing"),
        ("traverse", None),
    ),
)
def test_rejects_non_direction(
    method_name: str,
    direction: object,
) -> None:
    item = build_item("knowledge-a")
    graph = build_graph()
    method = getattr(graph, method_name)

    with pytest.raises(
        TypeError,
        match=(
            "direction must be a "
            "KnowledgeTraversalDirection"
        ),
    ):
        if method_name == "traverse":
            method(
                item,
                max_depth=1,
                direction=direction,
            )
        else:
            method(
                item,
                direction=direction,
            )


@pytest.mark.parametrize(
    "relation_types",
    (
        [],
        {
            KnowledgeRelationType.SUPPORTS,
        },
    ),
)
def test_rejects_non_tuple_relation_types(
    relation_types: object,
) -> None:
    graph = build_graph()

    with pytest.raises(
        TypeError,
        match=(
            "relation_types must be a tuple "
            "or None"
        ),
    ):
        graph.neighbors(
            build_item("knowledge-a"),
            relation_types=relation_types,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "relation_type",
    (
        "supports",
        None,
        1,
    ),
)
def test_rejects_invalid_relation_type_item(
    relation_type: object,
) -> None:
    graph = build_graph()

    with pytest.raises(
        TypeError,
        match=(
            "each relation type must be a "
            "KnowledgeRelationType"
        ),
    ):
        graph.neighbors(
            build_item("knowledge-a"),
            relation_types=(
                relation_type,  # type: ignore[arg-type]
            ),
        )


def test_rejects_duplicate_relation_types(
) -> None:
    graph = build_graph()

    with pytest.raises(
        ValueError,
        match=(
            "relation_types must not contain "
            "duplicates"
        ),
    ):
        graph.neighbors(
            build_item("knowledge-a"),
            relation_types=(
                KnowledgeRelationType.SUPPORTS,
                KnowledgeRelationType.SUPPORTS,
            ),
        )


@pytest.mark.parametrize(
    "max_depth",
    (
        True,
        1.5,
        "1",
    ),
)
def test_rejects_non_integer_max_depth(
    max_depth: object,
) -> None:
    graph = build_graph()

    with pytest.raises(
        TypeError,
        match="max_depth must be an integer",
    ):
        graph.traverse(
            build_item("knowledge-a"),
            max_depth=max_depth,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "max_depth",
    (
        -1,
        -2,
    ),
)
def test_rejects_negative_max_depth(
    max_depth: int,
) -> None:
    graph = build_graph()

    with pytest.raises(
        ValueError,
        match=(
            "max_depth must not be negative"
        ),
    ):
        graph.traverse(
            build_item("knowledge-a"),
            max_depth=max_depth,
        )
