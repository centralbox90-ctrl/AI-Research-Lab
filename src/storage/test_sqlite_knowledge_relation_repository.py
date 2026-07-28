from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from src.research.knowledge_item import KnowledgeItem
from src.research.knowledge_relation import (
    KnowledgeRelation,
    KnowledgeRelationType,
)
from src.research.knowledge_relation_repository import (
    KnowledgeRelationReferenceError,
    KnowledgeRelationRepository,
)
from src.research.knowledge_revision import (
    KnowledgeRevision,
)
from src.storage.sqlite_knowledge_relation_repository import (
    SqliteKnowledgeRelationRepository,
)
from src.storage.sqlite_knowledge_repository import (
    SqliteKnowledgeRepository,
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


def build_relation(
    *,
    source: KnowledgeItem,
    target: KnowledgeItem,
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


def build_repositories(
    tmp_path: Path,
    *items: KnowledgeItem,
) -> tuple[
    SqliteKnowledgeRepository,
    SqliteKnowledgeRelationRepository,
]:
    db_path = tmp_path / "knowledge.db"
    knowledge_repository = (
        SqliteKnowledgeRepository(db_path)
    )

    for item in sorted(
        items,
        key=lambda value: (
            value.id,
            value.version,
        ),
    ):
        knowledge_repository.save(
            KnowledgeRevision(
                item=item,
                valid_from=(
                    datetime(
                        2026,
                        1,
                        1,
                        tzinfo=timezone.utc,
                    )
                    + timedelta(
                        days=item.version
                    )
                ),
                change_reason=(
                    "Initial admission."
                    if item.version == 1
                    else "Updated evidence."
                ),
                supersedes_version=(
                    None
                    if item.version == 1
                    else item.version - 1
                ),
            )
        )

    return (
        knowledge_repository,
        SqliteKnowledgeRelationRepository(
            db_path=db_path,
            knowledge_repository=(
                knowledge_repository
            ),
        ),
    )


def build_three_items() -> tuple[
    KnowledgeItem,
    KnowledgeItem,
    KnowledgeItem,
]:
    return (
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
    )


def test_implements_repository_protocol(
    tmp_path: Path,
) -> None:
    _, repository = build_repositories(
        tmp_path
    )

    assert isinstance(
        repository,
        KnowledgeRelationRepository,
    )


def test_requires_knowledge_repository(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "knowledge_repository must implement "
            "KnowledgeRepository"
        ),
    ):
        SqliteKnowledgeRelationRepository(
            db_path=tmp_path / "knowledge.db",
            knowledge_repository=object(),
        )


def test_creates_parent_directory(
    tmp_path: Path,
) -> None:
    knowledge_repository = (
        SqliteKnowledgeRepository(
            tmp_path / "knowledge.db"
        )
    )
    relation_db_path = (
        tmp_path
        / "nested"
        / "relations.db"
    )

    SqliteKnowledgeRelationRepository(
        db_path=relation_db_path,
        knowledge_repository=(
            knowledge_repository
        ),
    )

    assert relation_db_path.is_file()


def test_persists_relations_across_instances(
    tmp_path: Path,
) -> None:
    item_a, item_b, _ = build_three_items()
    knowledge_repository, repository = (
        build_repositories(
            tmp_path,
            item_a,
            item_b,
        )
    )
    relation = build_relation(
        source=item_a,
        target=item_b,
    )
    repository.save(relation)

    reopened = (
        SqliteKnowledgeRelationRepository(
            db_path=tmp_path / "knowledge.db",
            knowledge_repository=(
                knowledge_repository
            ),
        )
    )

    assert reopened.list_all() == (
        relation,
    )


def test_lists_relations_in_deterministic_order(
    tmp_path: Path,
) -> None:
    item_a, item_b, item_c = build_three_items()
    _, repository = build_repositories(
        tmp_path,
        item_a,
        item_b,
        item_c,
    )
    supports = build_relation(
        source=item_a,
        target=item_b,
    )
    extends = build_relation(
        source=item_a,
        target=item_c,
        relation_type=(
            KnowledgeRelationType.EXTENDS
        ),
        reason="Adds a regime condition.",
    )
    derived = build_relation(
        source=item_c,
        target=item_b,
        relation_type=(
            KnowledgeRelationType.DERIVED_FROM
        ),
        reason="Uses the same evidence.",
    )

    repository.save(derived)
    repository.save(supports)
    repository.save(extends)

    assert repository.list_all() == (
        extends,
        supports,
        derived,
    )


def test_save_is_idempotent(
    tmp_path: Path,
) -> None:
    item_a, item_b, _ = build_three_items()
    _, repository = build_repositories(
        tmp_path,
        item_a,
        item_b,
    )
    relation = build_relation(
        source=item_a,
        target=item_b,
    )

    repository.save(relation)
    repository.save(relation)

    assert repository.list_all() == (
        relation,
    )


def test_preserves_distinct_reasons(
    tmp_path: Path,
) -> None:
    item_a, item_b, _ = build_three_items()
    _, repository = build_repositories(
        tmp_path,
        item_a,
        item_b,
    )
    first = build_relation(
        source=item_a,
        target=item_b,
        reason="Shared evidence.",
    )
    second = build_relation(
        source=item_a,
        target=item_b,
        reason="Independent confirmation.",
    )

    repository.save(first)
    repository.save(second)

    assert set(repository.list_all()) == {
        first,
        second,
    }


def test_rejects_non_relation(
    tmp_path: Path,
) -> None:
    _, repository = build_repositories(
        tmp_path
    )

    with pytest.raises(
        TypeError,
        match=(
            "relation must be a "
            "KnowledgeRelation"
        ),
    ):
        repository.save(object())


@pytest.mark.parametrize(
    "endpoint",
    (
        "source",
        "target",
    ),
)
def test_rejects_unstored_endpoint(
    tmp_path: Path,
    endpoint: str,
) -> None:
    item_a, item_b, _ = build_three_items()
    stored_items = (
        (item_b,)
        if endpoint == "source"
        else (item_a,)
    )
    _, repository = build_repositories(
        tmp_path,
        *stored_items,
    )
    relation = build_relation(
        source=item_a,
        target=item_b,
    )

    with pytest.raises(
        KnowledgeRelationReferenceError
    ) as error:
        repository.save(relation)

    assert error.value.endpoint == endpoint


def test_rejects_mismatched_endpoint_content(
    tmp_path: Path,
) -> None:
    stored_source = build_item(
        item_id="knowledge-a",
        statement="Stored statement A.",
    )
    incoming_source = build_item(
        item_id="knowledge-a",
        statement="Different statement A.",
    )
    target = build_item(
        item_id="knowledge-b",
        statement="Statement B.",
    )
    _, repository = build_repositories(
        tmp_path,
        stored_source,
        target,
    )
    relation = build_relation(
        source=incoming_source,
        target=target,
    )

    with pytest.raises(
        KnowledgeRelationReferenceError
    ) as error:
        repository.save(relation)

    assert error.value.endpoint == "source"
    assert error.value.item_id == (
        incoming_source.id
    )
    assert error.value.version == 1


def test_filters_outgoing_relations(
    tmp_path: Path,
) -> None:
    item_a, item_b, item_c = build_three_items()
    _, repository = build_repositories(
        tmp_path,
        item_a,
        item_b,
        item_c,
    )
    supports = build_relation(
        source=item_a,
        target=item_b,
    )
    extends = build_relation(
        source=item_a,
        target=item_c,
        relation_type=(
            KnowledgeRelationType.EXTENDS
        ),
        reason="Adds context.",
    )
    incoming = build_relation(
        source=item_c,
        target=item_a,
    )

    for relation in (
        incoming,
        supports,
        extends,
    ):
        repository.save(relation)

    assert repository.outgoing(
        " knowledge-a "
    ) == (
        extends,
        supports,
    )
    assert repository.outgoing(
        "knowledge-a",
        relation_type=(
            KnowledgeRelationType.SUPPORTS
        ),
    ) == (
        supports,
    )


def test_filters_incoming_relations(
    tmp_path: Path,
) -> None:
    item_a, item_b, item_c = build_three_items()
    _, repository = build_repositories(
        tmp_path,
        item_a,
        item_b,
        item_c,
    )
    relation_a = build_relation(
        source=item_a,
        target=item_c,
    )
    relation_b = build_relation(
        source=item_b,
        target=item_c,
    )
    repository.save(relation_b)
    repository.save(relation_a)

    assert repository.incoming(
        "knowledge-c"
    ) == (
        relation_a,
        relation_b,
    )


def test_filters_relations_by_exact_version(
    tmp_path: Path,
) -> None:
    item_a_v1 = build_item(
        item_id="knowledge-a",
        statement="Statement A.",
    )
    item_a_v2 = build_item(
        item_id="knowledge-a",
        statement="Updated statement A.",
        version=2,
    )
    item_b = build_item(
        item_id="knowledge-b",
        statement="Statement B.",
    )
    _, repository = build_repositories(
        tmp_path,
        item_a_v1,
        item_a_v2,
        item_b,
    )
    relation_v1 = build_relation(
        source=item_a_v1,
        target=item_b,
    )
    relation_v2 = build_relation(
        source=item_a_v2,
        target=item_b,
        reason="Updated evidence.",
    )
    repository.save(relation_v2)
    repository.save(relation_v1)

    assert repository.outgoing(
        "knowledge-a",
        version=2,
    ) == (
        relation_v2,
    )
    assert repository.relations_for(
        "knowledge-a",
        version=1,
    ) == (
        relation_v1,
    )


def test_relations_for_deduplicates_contradicts(
    tmp_path: Path,
) -> None:
    item_a, item_b, _ = build_three_items()
    _, repository = build_repositories(
        tmp_path,
        item_a,
        item_b,
    )
    contradiction = build_relation(
        source=item_b,
        target=item_a,
        relation_type=(
            KnowledgeRelationType.CONTRADICTS
        ),
        reason="Opposing evidence.",
    )
    repository.save(contradiction)

    assert repository.relations_for(
        "knowledge-a"
    ) == (
        contradiction,
    )
    assert repository.relations_for(
        "knowledge-b"
    ) == (
        contradiction,
    )


def test_returns_empty_queries_when_no_relations(
    tmp_path: Path,
) -> None:
    _, repository = build_repositories(
        tmp_path
    )

    assert repository.list_all() == ()
    assert repository.outgoing(
        "knowledge-a"
    ) == ()
    assert repository.incoming(
        "knowledge-a"
    ) == ()
    assert repository.relations_for(
        "knowledge-a"
    ) == ()


@pytest.mark.parametrize(
    "method_name",
    (
        "outgoing",
        "incoming",
        "relations_for",
    ),
)
def test_rejects_empty_item_id(
    tmp_path: Path,
    method_name: str,
) -> None:
    _, repository = build_repositories(
        tmp_path
    )
    method = getattr(
        repository,
        method_name,
    )

    with pytest.raises(
        ValueError,
        match="item_id must not be empty",
    ):
        method("   ")


@pytest.mark.parametrize(
    "version",
    (
        True,
        1.5,
        "1",
    ),
)
def test_rejects_non_integer_version(
    tmp_path: Path,
    version: object,
) -> None:
    _, repository = build_repositories(
        tmp_path
    )

    with pytest.raises(
        TypeError,
        match=(
            "version must be an integer "
            "or None"
        ),
    ):
        repository.outgoing(
            "knowledge-a",
            version=version,
        )


def test_rejects_non_positive_version(
    tmp_path: Path,
) -> None:
    _, repository = build_repositories(
        tmp_path
    )

    with pytest.raises(
        ValueError,
        match="version must be positive",
    ):
        repository.incoming(
            "knowledge-a",
            version=0,
        )


def test_rejects_invalid_relation_type(
    tmp_path: Path,
) -> None:
    _, repository = build_repositories(
        tmp_path
    )

    with pytest.raises(
        TypeError,
        match=(
            "relation_type must be a "
            "KnowledgeRelationType or None"
        ),
    ):
        repository.relations_for(
            "knowledge-a",
            relation_type="supports",
        )
