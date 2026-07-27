from datetime import datetime, timezone
from pathlib import Path

import pytest

from src.research.knowledge_applicability_query import (
    ApplicabilityMatchMode,
    KnowledgeApplicabilityQuery,
)
from src.research.knowledge_contradiction import (
    KnowledgeContradiction,
)
from src.research.knowledge_item import KnowledgeItem
from src.research.knowledge_repository import (
    KnowledgeItemConflictError,
    KnowledgeRepository,
    KnowledgeRevisionSequenceError,
)
from src.research.knowledge_revision import (
    KnowledgeRevision,
)
from src.storage.sqlite_knowledge_repository import (
    SqliteKnowledgeRepository,
)


def build_item(
    *,
    item_id: str = "knowledge-a",
    statement: str = "Statement A.",
    version: int = 1,
    applicability: tuple[str, ...] = (
        "liquid markets",
    ),
) -> KnowledgeItem:
    return KnowledgeItem(
        id=item_id,
        statement=statement,
        confidence=0.85,
        applicability=applicability,
        limitations=(
            "limited history",
        ),
        supporting_findings=(
            f"{item_id}-finding-a",
            f"{item_id}-finding-b",
        ),
        version=version,
        provenance=(
            (
                "knowledge_candidate_id",
                f"{item_id}-candidate",
            ),
        ),
    )


def build_revision(
    *,
    item_id: str = "knowledge-a",
    statement: str = "Statement A.",
    version: int = 1,
    day: int = 26,
    applicability: tuple[str, ...] = (
        "liquid markets",
    ),
) -> KnowledgeRevision:
    return KnowledgeRevision(
        item=build_item(
            item_id=item_id,
            statement=statement,
            version=version,
            applicability=applicability,
        ),
        valid_from=datetime(
            2026,
            7,
            day,
            tzinfo=timezone.utc,
        ),
        change_reason=(
            "Initial validation"
            if version == 1
            else "New supporting evidence"
        ),
        supersedes_version=(
            None
            if version == 1
            else version - 1
        ),
    )


def build_contradiction(
    left: KnowledgeRevision,
    right: KnowledgeRevision,
    *,
    reason: str = "Opposing conclusions.",
) -> KnowledgeContradiction:
    return KnowledgeContradiction(
        items=(
            left.item,
            right.item,
        ),
        reason=reason,
    )


def build_repository(
    tmp_path: Path,
) -> SqliteKnowledgeRepository:
    return SqliteKnowledgeRepository(
        db_path=tmp_path / "knowledge.db",
    )


def test_implements_knowledge_repository_protocol(
    tmp_path: Path,
) -> None:
    assert isinstance(
        build_repository(tmp_path),
        KnowledgeRepository,
    )


def test_creates_parent_directory(
    tmp_path: Path,
) -> None:
    db_path = (
        tmp_path
        / "nested"
        / "knowledge.db"
    )

    SqliteKnowledgeRepository(
        db_path=db_path
    )

    assert db_path.is_file()


def test_persists_revision_across_repository_instances(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "knowledge.db"
    revision = build_revision()
    SqliteKnowledgeRepository(
        db_path
    ).save(revision)

    reopened = SqliteKnowledgeRepository(
        db_path
    )

    assert reopened.get(
        revision.item.id
    ) == revision.item
    assert reopened.get_version(
        revision.item.id,
        revision.item.version,
    ) == revision
    assert reopened.history(
        revision.item.id
    ) == (revision,)


def test_returns_latest_item_and_complete_history(
    tmp_path: Path,
) -> None:
    repository = build_repository(tmp_path)
    first = build_revision()
    second = build_revision(
        statement="Updated statement.",
        version=2,
        day=27,
    )

    repository.save(first)
    repository.save(second)

    assert repository.get(
        first.item.id
    ) == second.item
    assert repository.history(
        first.item.id
    ) == (
        first,
        second,
    )


def test_returns_empty_results_for_unknown_item(
    tmp_path: Path,
) -> None:
    repository = build_repository(tmp_path)

    assert repository.get(
        "unknown-item"
    ) is None
    assert repository.get_version(
        "unknown-item",
        1,
    ) is None
    assert repository.history(
        "unknown-item"
    ) == ()


def test_lists_latest_items_in_id_order(
    tmp_path: Path,
) -> None:
    repository = build_repository(tmp_path)
    item_b = build_revision(
        item_id="knowledge-b",
        statement="Statement B.",
    )
    item_a_v1 = build_revision()
    item_a_v2 = build_revision(
        statement="Updated statement A.",
        version=2,
        day=27,
    )

    repository.save(item_b)
    repository.save(item_a_v1)
    repository.save(item_a_v2)

    assert repository.list_all() == (
        item_a_v2.item,
        item_b.item,
    )


def test_finds_matching_latest_items(
    tmp_path: Path,
) -> None:
    repository = build_repository(tmp_path)
    item_a_v1 = build_revision(
        applicability=(
            "liquid markets",
            "trend regime",
        ),
    )
    item_a_v2 = build_revision(
        statement="Updated statement A.",
        version=2,
        day=27,
        applicability=(
            "liquid markets",
            "range regime",
        ),
    )
    item_b = build_revision(
        item_id="knowledge-b",
        statement="Statement B.",
        applicability=(
            "trend regime",
            "liquid markets",
        ),
    )
    repository.save(item_a_v1)
    repository.save(item_b)
    repository.save(item_a_v2)

    query = KnowledgeApplicabilityQuery(
        terms=(
            "TREND REGIME",
            "liquid markets",
        ),
    )

    assert repository.find_applicable(
        query
    ) == (
        item_b.item,
    )


def test_finds_with_any_match_mode(
    tmp_path: Path,
) -> None:
    repository = build_repository(tmp_path)
    item_a = build_revision(
        applicability=(
            "crisis regime",
        ),
    )
    item_b = build_revision(
        item_id="knowledge-b",
        statement="Statement B.",
        applicability=(
            "trend regime",
        ),
    )
    repository.save(item_b)
    repository.save(item_a)

    query = KnowledgeApplicabilityQuery(
        terms=(
            "crisis regime",
            "trend regime",
        ),
        match_mode=ApplicabilityMatchMode.ANY,
    )

    assert repository.find_applicable(
        query
    ) == (
        item_a.item,
        item_b.item,
    )


def test_repeated_save_is_idempotent(
    tmp_path: Path,
) -> None:
    repository = build_repository(tmp_path)
    revision = build_revision()

    repository.save(revision)
    repository.save(revision)

    assert repository.history(
        revision.item.id
    ) == (revision,)


def test_rejects_conflicting_existing_version(
    tmp_path: Path,
) -> None:
    repository = build_repository(tmp_path)
    existing = build_revision()
    incoming = build_revision(
        statement="Changed statement.",
    )
    repository.save(existing)

    with pytest.raises(
        KnowledgeItemConflictError
    ) as error:
        repository.save(incoming)

    assert error.value.item_id == (
        existing.item.id
    )
    assert error.value.version == 1
    assert (
        error.value.existing_fingerprint
        == existing.fingerprint
    )
    assert (
        error.value.incoming_fingerprint
        == incoming.fingerprint
    )
    assert repository.history(
        existing.item.id
    ) == (existing,)


def test_rejects_non_initial_first_revision(
    tmp_path: Path,
) -> None:
    repository = build_repository(tmp_path)
    incoming = build_revision(
        version=2,
        day=27,
    )

    with pytest.raises(
        KnowledgeRevisionSequenceError
    ) as error:
        repository.save(incoming)

    assert error.value.expected_version == 1
    assert error.value.incoming_version == 2


def test_rejects_skipped_revision(
    tmp_path: Path,
) -> None:
    repository = build_repository(tmp_path)
    first = build_revision()
    third = build_revision(
        version=3,
        day=28,
    )
    repository.save(first)

    with pytest.raises(
        KnowledgeRevisionSequenceError
    ) as error:
        repository.save(third)

    assert error.value.expected_version == 2
    assert error.value.incoming_version == 3
    assert repository.history(
        first.item.id
    ) == (first,)


def test_rejects_non_increasing_valid_from(
    tmp_path: Path,
) -> None:
    repository = build_repository(tmp_path)
    first = build_revision()
    second = build_revision(
        version=2,
        day=26,
    )
    repository.save(first)

    with pytest.raises(
        ValueError,
        match=(
            "revision valid_from must be later "
            "than the latest stored revision"
        ),
    ):
        repository.save(second)

    assert repository.history(
        first.item.id
    ) == (first,)


def test_rejects_non_revision(
    tmp_path: Path,
) -> None:
    repository = build_repository(tmp_path)

    with pytest.raises(
        TypeError,
        match=(
            "revision must be a KnowledgeRevision"
        ),
    ):
        repository.save(
            object()
        )


def test_rejects_non_query(
    tmp_path: Path,
) -> None:
    repository = build_repository(tmp_path)

    with pytest.raises(
        TypeError,
        match=(
            "query must be a "
            "KnowledgeApplicabilityQuery"
        ),
    ):
        repository.find_applicable(
            object()
        )


def test_persists_contradictions_in_item_order(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "knowledge.db"
    repository = SqliteKnowledgeRepository(
        db_path
    )
    item_c = build_revision(
        item_id="knowledge-c",
        statement="Statement C.",
    )
    item_b = build_revision(
        item_id="knowledge-b",
        statement="Statement B.",
    )
    item_a = build_revision()
    repository.save(item_c)
    repository.save(item_b)
    repository.save(item_a)
    contradiction_bc = build_contradiction(
        item_b,
        item_c,
        reason="Conflict B-C.",
    )
    contradiction_ab = build_contradiction(
        item_a,
        item_b,
        reason="Conflict A-B.",
    )
    repository.save_contradiction(
        contradiction_bc
    )
    repository.save_contradiction(
        contradiction_ab
    )

    reopened = SqliteKnowledgeRepository(
        db_path
    )

    assert reopened.list_contradictions() == (
        contradiction_ab,
        contradiction_bc,
    )
    assert reopened.contradictions_for(
        " knowledge-b "
    ) == (
        contradiction_ab,
        contradiction_bc,
    )


def test_contradiction_save_is_idempotent(
    tmp_path: Path,
) -> None:
    repository = build_repository(tmp_path)
    left = build_revision()
    right = build_revision(
        item_id="knowledge-b",
        statement="Statement B.",
    )
    repository.save(left)
    repository.save(right)
    contradiction = build_contradiction(
        left,
        right,
    )

    repository.save_contradiction(
        contradiction
    )
    repository.save_contradiction(
        contradiction
    )

    assert repository.list_contradictions() == (
        contradiction,
    )


def test_retains_contradiction_after_superseding(
    tmp_path: Path,
) -> None:
    repository = build_repository(tmp_path)
    left_v1 = build_revision()
    right = build_revision(
        item_id="knowledge-b",
        statement="Statement B.",
    )
    left_v2 = build_revision(
        statement="Updated statement A.",
        version=2,
        day=27,
    )
    repository.save(left_v1)
    repository.save(right)
    contradiction = build_contradiction(
        left_v1,
        right,
    )
    repository.save_contradiction(
        contradiction
    )

    repository.save(left_v2)

    assert repository.get(
        left_v1.item.id
    ) == left_v2.item
    assert repository.list_contradictions() == (
        contradiction,
    )


def test_rejects_unstored_contradiction_item(
    tmp_path: Path,
) -> None:
    repository = build_repository(tmp_path)
    left = build_revision()
    right = build_revision(
        item_id="knowledge-b",
        statement="Statement B.",
    )
    repository.save(left)
    contradiction = build_contradiction(
        left,
        right,
    )

    with pytest.raises(
        ValueError,
        match=(
            "contradiction items must reference "
            "stored knowledge versions"
        ),
    ):
        repository.save_contradiction(
            contradiction
        )


def test_rejects_mismatched_contradiction_item(
    tmp_path: Path,
) -> None:
    repository = build_repository(tmp_path)
    stored_left = build_revision(
        statement="Stored statement A.",
    )
    incoming_left = build_revision(
        statement="Different statement A.",
    )
    right = build_revision(
        item_id="knowledge-b",
        statement="Statement B.",
    )
    repository.save(stored_left)
    repository.save(right)
    contradiction = build_contradiction(
        incoming_left,
        right,
    )

    with pytest.raises(
        ValueError,
        match=(
            "contradiction items must reference "
            "stored knowledge versions"
        ),
    ):
        repository.save_contradiction(
            contradiction
        )


def test_rejects_non_contradiction(
    tmp_path: Path,
) -> None:
    repository = build_repository(tmp_path)

    with pytest.raises(
        TypeError,
        match=(
            "contradiction must be a "
            "KnowledgeContradiction"
        ),
    ):
        repository.save_contradiction(
            object()
        )


@pytest.mark.parametrize(
    "item_id",
    (
        "",
        "   ",
    ),
)
def test_rejects_empty_item_id(
    tmp_path: Path,
    item_id: str,
) -> None:
    repository = build_repository(tmp_path)

    with pytest.raises(
        ValueError,
        match="item_id must not be empty",
    ):
        repository.history(item_id)


@pytest.mark.parametrize(
    ("version", "expected_exception"),
    (
        (True, TypeError),
        (1.5, TypeError),
        ("1", TypeError),
        (0, ValueError),
        (-1, ValueError),
    ),
)
def test_rejects_invalid_version_lookup(
    tmp_path: Path,
    version: object,
    expected_exception: type[Exception],
) -> None:
    repository = build_repository(tmp_path)

    with pytest.raises(expected_exception):
        repository.get_version(
            "knowledge-a",
            version,
        )
