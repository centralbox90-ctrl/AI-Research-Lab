from datetime import datetime, timezone

import pytest

from src.application.in_memory_knowledge_relation_repository import (
    InMemoryKnowledgeRelationRepository,
)
from src.application.in_memory_knowledge_repository import (
    InMemoryKnowledgeRepository,
)
from src.application.knowledge_graph_relation_registrar import (
    KnowledgeGraphRelationRegistrar,
)
from src.research.knowledge_contradiction import (
    KnowledgeContradiction,
)
from src.research.knowledge_graph import (
    KnowledgeGraph,
    KnowledgeTraversalDirection,
)
from src.research.knowledge_item import KnowledgeItem
from src.research.knowledge_relation import (
    KnowledgeRelationType,
)
from src.research.knowledge_revision import (
    KnowledgeRevision,
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


def build_revision(
    item: KnowledgeItem,
    *,
    day: int,
    change_reason: str,
) -> KnowledgeRevision:
    return KnowledgeRevision(
        item=item,
        valid_from=datetime(
            2026,
            1,
            day,
            tzinfo=timezone.utc,
        ),
        change_reason=change_reason,
        supersedes_version=(
            None
            if item.version == 1
            else item.version - 1
        ),
    )


def build_registrar(
) -> tuple[
    InMemoryKnowledgeRepository,
    InMemoryKnowledgeRelationRepository,
    KnowledgeGraphRelationRegistrar,
]:
    knowledge_repository = (
        InMemoryKnowledgeRepository()
    )
    relation_repository = (
        InMemoryKnowledgeRelationRepository(
            knowledge_repository
        )
    )

    return (
        knowledge_repository,
        relation_repository,
        KnowledgeGraphRelationRegistrar(
            knowledge_repository=(
                knowledge_repository
            ),
            relation_repository=(
                relation_repository
            ),
        ),
    )


def save_initial(
    repository: InMemoryKnowledgeRepository,
    item: KnowledgeItem,
) -> KnowledgeRevision:
    revision = build_revision(
        item,
        day=1,
        change_reason="Initial admission.",
    )
    repository.save(revision)
    return revision


def test_requires_knowledge_repository() -> None:
    knowledge_repository = (
        InMemoryKnowledgeRepository()
    )
    relation_repository = (
        InMemoryKnowledgeRelationRepository(
            knowledge_repository
        )
    )

    with pytest.raises(
        TypeError,
        match=(
            "knowledge_repository must implement "
            "KnowledgeRepository"
        ),
    ):
        KnowledgeGraphRelationRegistrar(
            knowledge_repository=object(),  # type: ignore[arg-type]
            relation_repository=(
                relation_repository
            ),
        )


def test_requires_relation_repository() -> None:
    knowledge_repository = (
        InMemoryKnowledgeRepository()
    )

    with pytest.raises(
        TypeError,
        match=(
            "relation_repository must implement "
            "KnowledgeRelationRepository"
        ),
    ):
        KnowledgeGraphRelationRegistrar(
            knowledge_repository=(
                knowledge_repository
            ),
            relation_repository=object(),  # type: ignore[arg-type]
        )


def test_projects_registered_contradiction(
) -> None:
    (
        knowledge_repository,
        relation_repository,
        registrar,
    ) = build_registrar()
    item_a = build_item(
        item_id="knowledge-a",
        statement="Momentum persists.",
    )
    item_b = build_item(
        item_id="knowledge-b",
        statement="Momentum does not persist.",
    )
    save_initial(knowledge_repository, item_a)
    save_initial(knowledge_repository, item_b)
    contradiction = KnowledgeContradiction(
        items=(item_b, item_a),
        reason="Opposing conclusions.",
    )
    knowledge_repository.save_contradiction(
        contradiction
    )

    relation = registrar.register_contradiction(
        contradiction
    )

    assert relation.source is item_a
    assert relation.target is item_b
    assert (
        relation.relation_type
        is KnowledgeRelationType.CONTRADICTS
    )
    assert relation.reason == (
        "Opposing conclusions."
    )
    assert relation_repository.list_all() == (
        relation,
    )


def test_contradiction_projection_is_idempotent(
) -> None:
    (
        knowledge_repository,
        relation_repository,
        registrar,
    ) = build_registrar()
    item_a = build_item(
        item_id="knowledge-a",
        statement="Statement A.",
    )
    item_b = build_item(
        item_id="knowledge-b",
        statement="Statement B.",
    )
    save_initial(knowledge_repository, item_a)
    save_initial(knowledge_repository, item_b)
    contradiction = KnowledgeContradiction(
        items=(item_a, item_b),
        reason="Opposing conclusions.",
    )
    knowledge_repository.save_contradiction(
        contradiction
    )

    first = registrar.register_contradiction(
        contradiction
    )
    second = registrar.register_contradiction(
        contradiction
    )

    assert first == second
    assert relation_repository.list_all() == (
        first,
    )


def test_rejects_non_contradiction() -> None:
    _, _, registrar = build_registrar()

    with pytest.raises(
        TypeError,
        match=(
            "contradiction must be a "
            "KnowledgeContradiction"
        ),
    ):
        registrar.register_contradiction(
            object(),  # type: ignore[arg-type]
        )


def test_requires_registered_contradiction(
) -> None:
    (
        knowledge_repository,
        relation_repository,
        registrar,
    ) = build_registrar()
    item_a = build_item(
        item_id="knowledge-a",
        statement="Statement A.",
    )
    item_b = build_item(
        item_id="knowledge-b",
        statement="Statement B.",
    )
    save_initial(knowledge_repository, item_a)
    save_initial(knowledge_repository, item_b)
    contradiction = KnowledgeContradiction(
        items=(item_a, item_b),
        reason="Opposing conclusions.",
    )

    with pytest.raises(
        ValueError,
        match=(
            "contradiction must be registered "
            "before graph projection"
        ),
    ):
        registrar.register_contradiction(
            contradiction
        )

    assert relation_repository.list_all() == ()


def test_initial_revision_creates_no_relation(
) -> None:
    (
        knowledge_repository,
        relation_repository,
        registrar,
    ) = build_registrar()
    revision = save_initial(
        knowledge_repository,
        build_item(
            item_id="knowledge-a",
            statement="Statement A.",
        ),
    )

    assert registrar.register_revision(
        revision
    ) is None
    assert relation_repository.list_all() == ()


def test_projects_superseding_revision(
) -> None:
    (
        knowledge_repository,
        relation_repository,
        registrar,
    ) = build_registrar()
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
    save_initial(knowledge_repository, older)
    revision = build_revision(
        newer,
        day=2,
        change_reason="Updated evidence.",
    )
    knowledge_repository.save(revision)

    relation = registrar.register_revision(
        revision
    )

    assert relation is not None
    assert relation.source is newer
    assert relation.target is older
    assert (
        relation.relation_type
        is KnowledgeRelationType.SUPERSEDES
    )
    assert relation.reason == "Updated evidence."
    assert relation_repository.list_all() == (
        relation,
    )


def test_each_revision_supersedes_immediate_version(
) -> None:
    (
        knowledge_repository,
        _,
        registrar,
    ) = build_registrar()
    item_v1 = build_item(
        item_id="knowledge-a",
        statement="Statement A.",
        version=1,
    )
    item_v2 = build_item(
        item_id="knowledge-a",
        statement="Statement A v2.",
        version=2,
    )
    item_v3 = build_item(
        item_id="knowledge-a",
        statement="Statement A v3.",
        version=3,
    )
    save_initial(knowledge_repository, item_v1)
    revision_v2 = build_revision(
        item_v2,
        day=2,
        change_reason="Second version.",
    )
    revision_v3 = build_revision(
        item_v3,
        day=3,
        change_reason="Third version.",
    )
    knowledge_repository.save(revision_v2)
    knowledge_repository.save(revision_v3)

    relation_v2 = registrar.register_revision(
        revision_v2
    )
    relation_v3 = registrar.register_revision(
        revision_v3
    )

    assert relation_v2 is not None
    assert relation_v3 is not None
    assert relation_v2.target is item_v1
    assert relation_v3.target is item_v2


def test_revision_projection_is_idempotent(
) -> None:
    (
        knowledge_repository,
        relation_repository,
        registrar,
    ) = build_registrar()
    older = build_item(
        item_id="knowledge-a",
        statement="Statement A.",
        version=1,
    )
    newer = build_item(
        item_id="knowledge-a",
        statement="Statement A v2.",
        version=2,
    )
    save_initial(knowledge_repository, older)
    revision = build_revision(
        newer,
        day=2,
        change_reason="Updated evidence.",
    )
    knowledge_repository.save(revision)

    first = registrar.register_revision(
        revision
    )
    second = registrar.register_revision(
        revision
    )

    assert first == second
    assert first is not None
    assert relation_repository.list_all() == (
        first,
    )


def test_rejects_non_revision() -> None:
    _, _, registrar = build_registrar()

    with pytest.raises(
        TypeError,
        match=(
            "revision must be a "
            "KnowledgeRevision"
        ),
    ):
        registrar.register_revision(
            object(),  # type: ignore[arg-type]
        )


def test_requires_stored_revision() -> None:
    (
        _,
        relation_repository,
        registrar,
    ) = build_registrar()
    revision = build_revision(
        build_item(
            item_id="knowledge-a",
            statement="Statement A.",
        ),
        day=1,
        change_reason="Initial admission.",
    )

    with pytest.raises(
        ValueError,
        match=(
            "revision must be stored before "
            "graph projection"
        ),
    ):
        registrar.register_revision(revision)

    assert relation_repository.list_all() == ()


def test_requires_exact_stored_revision(
) -> None:
    (
        knowledge_repository,
        relation_repository,
        registrar,
    ) = build_registrar()
    item = build_item(
        item_id="knowledge-a",
        statement="Statement A.",
    )
    stored = build_revision(
        item,
        day=1,
        change_reason="Initial admission.",
    )
    conflicting = build_revision(
        item,
        day=2,
        change_reason="Different admission.",
    )
    knowledge_repository.save(stored)

    with pytest.raises(
        ValueError,
        match=(
            "revision must be stored before "
            "graph projection"
        ),
    ):
        registrar.register_revision(
            conflicting
        )

    assert relation_repository.list_all() == ()


def test_contradiction_projection_is_visible_in_graph(
) -> None:
    (
        knowledge_repository,
        relation_repository,
        registrar,
    ) = build_registrar()
    item_a = build_item(
        item_id="knowledge-a",
        statement="Statement A.",
    )
    item_b = build_item(
        item_id="knowledge-b",
        statement="Statement B.",
    )
    save_initial(knowledge_repository, item_a)
    save_initial(knowledge_repository, item_b)
    contradiction = KnowledgeContradiction(
        items=(item_a, item_b),
        reason="Opposing conclusions.",
    )
    knowledge_repository.save_contradiction(
        contradiction
    )
    registrar.register_contradiction(
        contradiction
    )
    graph = KnowledgeGraph(
        relation_repository
    )

    assert graph.neighbors(item_a) == (
        item_b,
    )
    assert graph.neighbors(item_b) == (
        item_a,
    )


def test_supersedes_projection_is_traversable(
) -> None:
    (
        knowledge_repository,
        relation_repository,
        registrar,
    ) = build_registrar()
    older = build_item(
        item_id="knowledge-a",
        statement="Statement A.",
        version=1,
    )
    newer = build_item(
        item_id="knowledge-a",
        statement="Statement A v2.",
        version=2,
    )
    save_initial(knowledge_repository, older)
    revision = build_revision(
        newer,
        day=2,
        change_reason="Updated evidence.",
    )
    knowledge_repository.save(revision)
    registrar.register_revision(revision)
    graph = KnowledgeGraph(
        relation_repository
    )

    assert graph.traverse(
        newer,
        max_depth=1,
        direction=(
            KnowledgeTraversalDirection.OUTGOING
        ),
        relation_types=(
            KnowledgeRelationType.SUPERSEDES,
        ),
    ) == (older,)
