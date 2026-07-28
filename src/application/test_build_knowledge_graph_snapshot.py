from __future__ import annotations

from datetime import UTC, datetime

import pytest

from src.application.build_knowledge_graph_snapshot import (
    BuildKnowledgeGraphSnapshot,
)
from src.application.in_memory_knowledge_relation_repository import (
    InMemoryKnowledgeRelationRepository,
)
from src.application.in_memory_knowledge_repository import (
    InMemoryKnowledgeRepository,
)
from src.application.knowledge_graph_relation_registrar import (
    KnowledgeGraphRelationRegistrar,
)
from src.research.knowledge_item import (
    KnowledgeItem,
)
from src.research.knowledge_relation import (
    KnowledgeRelationType,
)
from src.research.knowledge_revision import (
    KnowledgeRevision,
)


def _item(
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
            f"{item_id}-finding-1",
            f"{item_id}-finding-2",
        ),
        version=version,
        provenance=(("producer", "test"),),
    )


def _revision(
    item: KnowledgeItem,
    *,
    hour: int,
) -> KnowledgeRevision:
    return KnowledgeRevision(
        item=item,
        valid_from=datetime(
            2026,
            7,
            28,
            hour,
            0,
            tzinfo=UTC,
        ),
        change_reason=(
            "Initial knowledge."
            if item.version == 1
            else "Updated knowledge."
        ),
        supersedes_version=(
            None
            if item.version == 1
            else item.version - 1
        ),
    )


def _builder(
) -> tuple[
    InMemoryKnowledgeRepository,
    InMemoryKnowledgeRelationRepository,
    BuildKnowledgeGraphSnapshot,
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
        BuildKnowledgeGraphSnapshot(
            knowledge_repository=(
                knowledge_repository
            ),
            relation_repository=(
                relation_repository
            ),
        ),
    )


def test_builds_empty_snapshot():
    _, _, builder = _builder()

    snapshot = builder.execute()

    assert snapshot.items == ()
    assert snapshot.relations == ()


def test_includes_isolated_latest_item():
    repository, _, builder = _builder()
    item = _item(
        item_id="knowledge-1",
        statement="Momentum persists.",
    )
    repository.save(
        _revision(
            item,
            hour=10,
        )
    )

    snapshot = builder.execute()

    assert snapshot.items == (item,)
    assert snapshot.relations == ()


def test_includes_historical_relation_endpoints():
    (
        knowledge_repository,
        relation_repository,
        builder,
    ) = _builder()
    older = _item(
        item_id="knowledge-1",
        statement="Momentum may persist.",
        version=1,
    )
    newer = _item(
        item_id="knowledge-1",
        statement="Momentum persists.",
        version=2,
    )
    knowledge_repository.save(
        _revision(
            older,
            hour=10,
        )
    )
    newer_revision = _revision(
        newer,
        hour=11,
    )
    knowledge_repository.save(
        newer_revision
    )
    registrar = KnowledgeGraphRelationRegistrar(
        knowledge_repository=(
            knowledge_repository
        ),
        relation_repository=(
            relation_repository
        ),
    )
    relation = registrar.register_revision(
        newer_revision
    )

    snapshot = builder.execute()

    assert relation is not None
    assert snapshot.items == (
        older,
        newer,
    )
    assert snapshot.relations == (
        relation,
    )
    assert (
        snapshot.relations[0].relation_type
        is KnowledgeRelationType.SUPERSEDES
    )


@pytest.mark.parametrize(
    "dependency",
    (
        "knowledge_repository",
        "relation_repository",
    ),
)
def test_requires_repository_ports(
    dependency: str,
):
    knowledge_repository = (
        InMemoryKnowledgeRepository()
    )
    relation_repository = (
        InMemoryKnowledgeRelationRepository(
            knowledge_repository
        )
    )
    arguments = {
        "knowledge_repository": (
            knowledge_repository
        ),
        "relation_repository": (
            relation_repository
        ),
    }
    arguments[dependency] = object()

    with pytest.raises(TypeError):
        BuildKnowledgeGraphSnapshot(
            **arguments
        )
