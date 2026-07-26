from datetime import datetime, timedelta, timezone

import pytest

from src.application.in_memory_knowledge_relation_repository import (
    InMemoryKnowledgeRelationRepository,
)
from src.application.in_memory_knowledge_repository import (
    InMemoryKnowledgeRepository,
)
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
    *items: KnowledgeItem,
) -> tuple[
    InMemoryKnowledgeRepository,
    InMemoryKnowledgeRelationRepository,
]:
    knowledge_repository = (
        InMemoryKnowledgeRepository()
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
        InMemoryKnowledgeRelationRepository(
            knowledge_repository
        ),
    )


def test_implements_repository_protocol() -> None:
    _, repository = build_repositories()

    assert isinstance(
        repository,
        KnowledgeRelationRepository,
    )


def test_requires_knowledge_repository() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "knowledge_repository must implement "
            "KnowledgeRepository"
        ),
    ):
        InMemoryKnowledgeRelationRepository(
            object(),  # type: ignore[arg-type]
        )


def test_lists_relations_in_deterministic_order(
) -> None:
    item_a = build_item(
        item_id="knowledge-a",
        statement="Statement A.",
    )
    item_b = build_item(
        item_id="knowledge-b",
        statement="Statement B.",
    )
    item_c = build_item(
        item_id="knowledge-c",
        statement="Statement C.",
    )
    _, repository = build_repositories(
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


def test_save_is_idempotent() -> None:
    item_a = build_item(
        item_id="knowledge-a",
        statement="Statement A.",
    )
    item_b = build_item(
        item_id="knowledge-b",
        statement="Statement B.",
    )
    _, repository = build_repositories(
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


def test_preserves_distinct_reasons() -> None:
    item_a = build_item(
        item_id="knowledge-a",
        statement="Statement A.",
    )
    item_b = build_item(
        item_id="knowledge-b",
        statement="Statement B.",
    )
    _, repository = build_repositories(
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


def test_rejects_non_relation() -> None:
    _, repository = build_repositories()

    with pytest.raises(
        TypeError,
        match=(
            "relation must be a "
            "KnowledgeRelation"
        ),
    ):
        repository.save(
            object(),  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "missing_endpoint",
    (
        "source",
        "target",
    ),
)
def test_rejects_unstored_endpoint(
    missing_endpoint: str,
) -> None:
    stored = build_item(
        item_id="knowledge-stored",
        statement="Stored statement.",
    )
    missing = build_item(
        item_id="knowledge-missing",
        statement="Missing statement.",
    )
    _, repository = build_repositories(
        stored
    )
    relation = build_relation(
        source=(
            missing
            if missing_endpoint == "source"
            else stored
        ),
        target=(
            missing
            if missing_endpoint == "target"
            else stored
        ),
    )

    with pytest.raises(
        KnowledgeRelationReferenceError,
    ) as error:
        repository.save(relation)

    assert error.value.endpoint == missing_endpoint
    assert (
        error.value.item_id
        == "knowledge-missing"
    )
    assert error.value.version == 1
    assert repository.list_all() == ()


def test_rejects_mismatched_endpoint_fingerprint(
) -> None:
    stored_a = build_item(
        item_id="knowledge-a",
        statement="Stored statement A.",
    )
    conflicting_a = build_item(
        item_id="knowledge-a",
        statement="Conflicting statement A.",
    )
    item_b = build_item(
        item_id="knowledge-b",
        statement="Statement B.",
    )
    _, repository = build_repositories(
        stored_a,
        item_b,
    )

    with pytest.raises(
        KnowledgeRelationReferenceError,
    ) as error:
        repository.save(
            build_relation(
                source=conflicting_a,
                target=item_b,
            )
        )

    assert error.value.endpoint == "source"
    assert error.value.item_id == "knowledge-a"
    assert error.value.version == 1


def test_retains_relation_to_historical_version(
) -> None:
    item_a_v1 = build_item(
        item_id="knowledge-a",
        statement="Statement A.",
        version=1,
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
        item_a_v1,
        item_a_v2,
        item_b,
    )
    relation = build_relation(
        source=item_a_v1,
        target=item_b,
    )

    repository.save(relation)

    assert repository.list_all() == (
        relation,
    )
    assert repository.outgoing(
        "knowledge-a",
        version=1,
    ) == (relation,)
    assert repository.outgoing(
        "knowledge-a",
        version=2,
    ) == ()


def test_outgoing_is_deterministic() -> None:
    item_a = build_item(
        item_id="knowledge-a",
        statement="Statement A.",
    )
    item_b = build_item(
        item_id="knowledge-b",
        statement="Statement B.",
    )
    item_c = build_item(
        item_id="knowledge-c",
        statement="Statement C.",
    )
    _, repository = build_repositories(
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

    repository.save(supports)
    repository.save(extends)

    assert repository.outgoing(
        "knowledge-a"
    ) == (
        extends,
        supports,
    )


def test_incoming_is_deterministic() -> None:
    item_a = build_item(
        item_id="knowledge-a",
        statement="Statement A.",
    )
    item_b = build_item(
        item_id="knowledge-b",
        statement="Statement B.",
    )
    item_c = build_item(
        item_id="knowledge-c",
        statement="Statement C.",
    )
    _, repository = build_repositories(
        item_a,
        item_b,
        item_c,
    )
    from_a = build_relation(
        source=item_a,
        target=item_b,
    )
    from_c = build_relation(
        source=item_c,
        target=item_b,
    )

    repository.save(from_c)
    repository.save(from_a)

    assert repository.incoming(
        "knowledge-b"
    ) == (
        from_a,
        from_c,
    )


def test_relations_for_returns_both_directions(
) -> None:
    item_a = build_item(
        item_id="knowledge-a",
        statement="Statement A.",
    )
    item_b = build_item(
        item_id="knowledge-b",
        statement="Statement B.",
    )
    item_c = build_item(
        item_id="knowledge-c",
        statement="Statement C.",
    )
    _, repository = build_repositories(
        item_a,
        item_b,
        item_c,
    )
    outgoing = build_relation(
        source=item_b,
        target=item_c,
    )
    incoming = build_relation(
        source=item_a,
        target=item_b,
    )

    repository.save(outgoing)
    repository.save(incoming)

    assert repository.relations_for(
        "knowledge-b"
    ) == (
        incoming,
        outgoing,
    )


def test_relations_for_does_not_duplicate_same_id_edge(
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
    _, repository = build_repositories(
        older,
        newer,
    )
    relation = build_relation(
        source=newer,
        target=older,
        relation_type=(
            KnowledgeRelationType.SUPERSEDES
        ),
        reason="Updated evidence.",
    )

    repository.save(relation)

    assert repository.relations_for(
        "knowledge-a"
    ) == (relation,)


@pytest.mark.parametrize(
    "method_name",
    (
        "outgoing",
        "incoming",
        "relations_for",
    ),
)
def test_filters_by_exact_version(
    method_name: str,
) -> None:
    item_a_v1 = build_item(
        item_id="knowledge-a",
        statement="Statement A.",
        version=1,
    )
    item_a_v2 = build_item(
        item_id="knowledge-a",
        statement="Updated statement A.",
        version=2,
    )
    item_b_v1 = build_item(
        item_id="knowledge-b",
        statement="Statement B.",
        version=1,
    )
    item_b_v2 = build_item(
        item_id="knowledge-b",
        statement="Updated statement B.",
        version=2,
    )
    _, repository = build_repositories(
        item_a_v1,
        item_a_v2,
        item_b_v1,
        item_b_v2,
    )
    first = build_relation(
        source=item_a_v1,
        target=item_b_v1,
    )
    second = build_relation(
        source=item_a_v2,
        target=item_b_v2,
        relation_type=(
            KnowledgeRelationType.EXTENDS
        ),
        reason="Updated relation.",
    )
    repository.save(second)
    repository.save(first)

    method = getattr(
        repository,
        method_name,
    )
    query_id = (
        "knowledge-b"
        if method_name == "incoming"
        else "knowledge-a"
    )

    assert method(
        query_id,
        version=1,
    ) == (first,)


@pytest.mark.parametrize(
    "method_name",
    (
        "outgoing",
        "incoming",
        "relations_for",
    ),
)
def test_filters_by_relation_type(
    method_name: str,
) -> None:
    item_a = build_item(
        item_id="knowledge-a",
        statement="Statement A.",
    )
    item_b = build_item(
        item_id="knowledge-b",
        statement="Statement B.",
    )
    item_c = build_item(
        item_id="knowledge-c",
        statement="Statement C.",
    )
    _, repository = build_repositories(
        item_a,
        item_b,
        item_c,
    )
    supports = build_relation(
        source=item_a,
        target=item_b,
    )
    extends_from_a = build_relation(
        source=item_a,
        target=item_c,
        relation_type=(
            KnowledgeRelationType.EXTENDS
        ),
        reason="Extends C.",
    )
    extends_to_b = build_relation(
        source=item_c,
        target=item_b,
        relation_type=(
            KnowledgeRelationType.EXTENDS
        ),
        reason="Extends B.",
    )

    repository.save(extends_to_b)
    repository.save(extends_from_a)
    repository.save(supports)

    method = getattr(
        repository,
        method_name,
    )
    query_id = (
        "knowledge-b"
        if method_name != "outgoing"
        else "knowledge-a"
    )

    assert method(
        query_id,
        relation_type=(
            KnowledgeRelationType.SUPPORTS
        ),
    ) == (supports,)


@pytest.mark.parametrize(
    "method_name",
    (
        "outgoing",
        "incoming",
        "relations_for",
    ),
)
def test_unknown_item_returns_empty(
    method_name: str,
) -> None:
    _, repository = build_repositories()
    method = getattr(
        repository,
        method_name,
    )

    assert method("knowledge-unknown") == ()


def test_normalizes_query_item_id() -> None:
    item_a = build_item(
        item_id="knowledge-a",
        statement="Statement A.",
    )
    item_b = build_item(
        item_id="knowledge-b",
        statement="Statement B.",
    )
    _, repository = build_repositories(
        item_a,
        item_b,
    )
    relation = build_relation(
        source=item_a,
        target=item_b,
    )
    repository.save(relation)

    assert repository.outgoing(
        "  knowledge-a  "
    ) == (relation,)


@pytest.mark.parametrize(
    "item_id",
    (
        None,
        1,
        True,
    ),
)
def test_rejects_non_string_item_id(
    item_id: object,
) -> None:
    _, repository = build_repositories()

    with pytest.raises(
        TypeError,
        match="item_id must be a string",
    ):
        repository.outgoing(
            item_id,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "item_id",
    (
        "",
        "   ",
    ),
)
def test_rejects_empty_item_id(
    item_id: str,
) -> None:
    _, repository = build_repositories()

    with pytest.raises(
        ValueError,
        match="item_id must not be empty",
    ):
        repository.incoming(item_id)


@pytest.mark.parametrize(
    "version",
    (
        True,
        1.5,
        "1",
    ),
)
def test_rejects_non_integer_version(
    version: object,
) -> None:
    _, repository = build_repositories()

    with pytest.raises(
        TypeError,
        match=(
            "version must be an integer "
            "or None"
        ),
    ):
        repository.relations_for(
            "knowledge-a",
            version=version,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "version",
    (
        0,
        -1,
    ),
)
def test_rejects_non_positive_version(
    version: int,
) -> None:
    _, repository = build_repositories()

    with pytest.raises(
        ValueError,
        match="version must be positive",
    ):
        repository.outgoing(
            "knowledge-a",
            version=version,
        )


@pytest.mark.parametrize(
    "relation_type",
    (
        "supports",
        1,
    ),
)
def test_rejects_non_relation_type(
    relation_type: object,
) -> None:
    _, repository = build_repositories()

    with pytest.raises(
        TypeError,
        match=(
            "relation_type must be a "
            "KnowledgeRelationType or None"
        ),
    ):
        repository.incoming(
            "knowledge-a",
            relation_type=relation_type,  # type: ignore[arg-type]
        )
