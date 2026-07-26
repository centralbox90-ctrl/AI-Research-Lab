from datetime import datetime, timezone

import pytest

from src.application.in_memory_knowledge_repository import (
    InMemoryKnowledgeRepository,
)
from src.research.knowledge_candidate import (
    KnowledgeCandidate,
)
from src.research.knowledge_candidate_validator import (
    KnowledgeCandidateValidator,
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


def build_item(
    *,
    item_id: str = "knowledge-a",
    statement: str = "Statement A.",
    version: int = 1,
) -> KnowledgeItem:
    return KnowledgeItem(
        id=item_id,
        statement=statement,
        confidence=0.85,
        applicability=(
            "liquid markets",
        ),
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
) -> KnowledgeRevision:
    return KnowledgeRevision(
        item=build_item(
            item_id=item_id,
            statement=statement,
            version=version,
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


def test_implements_knowledge_repository_protocol(
) -> None:
    repository = InMemoryKnowledgeRepository()

    assert isinstance(
        repository,
        KnowledgeRepository,
    )


def test_stores_item_admitted_from_knowledge_candidate(
) -> None:
    candidate = KnowledgeCandidate(
        id="candidate-momentum",
        statement=(
            "Momentum persists in liquid trend regimes."
        ),
        confidence=0.85,
        applicability=(
            "liquid equity indices",
        ),
        limitations=(
            "not evaluated in crisis regimes",
        ),
        supporting_findings=(
            "finding-a",
            "finding-b",
        ),
        hypothesis_evaluation_ref=(
            "hypothesis-evaluation-123"
        ),
        provenance=(
            ("dataset_fingerprint", "dataset-123"),
        ),
    )
    item = KnowledgeCandidateValidator(
        minimum_confidence=0.75,
        minimum_supporting_findings=2,
    ).validate(candidate=candidate)
    revision = KnowledgeRevision(
        item=item,
        valid_from=datetime(
            2026,
            7,
            26,
            tzinfo=timezone.utc,
        ),
        change_reason="Initial validation",
        supersedes_version=None,
    )
    repository = InMemoryKnowledgeRepository()

    repository.save(revision)

    assert repository.get(item.id) is item
    assert repository.history(item.id) == (
        revision,
    )
    assert dict(item.provenance)[
        "knowledge_candidate_fingerprint"
    ] == candidate.fingerprint


def test_returns_latest_item_and_complete_history(
) -> None:
    repository = InMemoryKnowledgeRepository()
    first = build_revision()
    second = build_revision(
        statement="Updated statement.",
        version=2,
        day=27,
    )

    repository.save(first)
    repository.save(second)

    assert repository.get(first.item.id) is (
        second.item
    )
    assert repository.get_version(
        first.item.id,
        1,
    ) is first
    assert repository.get_version(
        first.item.id,
        2,
    ) is second
    assert repository.history(first.item.id) == (
        first,
        second,
    )


def test_returns_empty_results_for_unknown_item(
) -> None:
    repository = InMemoryKnowledgeRepository()

    assert repository.get("unknown-item") is None
    assert repository.get_version(
        "unknown-item",
        1,
    ) is None
    assert repository.history("unknown-item") == ()


def test_lists_latest_items_in_deterministic_id_order(
) -> None:
    repository = InMemoryKnowledgeRepository()
    item_b_v1 = build_revision(
        item_id="knowledge-b",
        statement="Statement B.",
    )
    item_a_v1 = build_revision(
        item_id="knowledge-a",
        statement="Statement A.",
    )
    item_a_v2 = build_revision(
        item_id="knowledge-a",
        statement="Updated statement A.",
        version=2,
        day=27,
    )

    repository.save(item_b_v1)
    repository.save(item_a_v1)
    repository.save(item_a_v2)

    assert repository.list_all() == (
        item_a_v2.item,
        item_b_v1.item,
    )


def test_repeated_save_of_same_revision_is_idempotent(
) -> None:
    repository = InMemoryKnowledgeRepository()
    revision = build_revision()

    repository.save(revision)
    repository.save(revision)

    assert repository.history(
        revision.item.id
    ) == (revision,)


def test_rejects_conflicting_content_for_existing_version(
) -> None:
    repository = InMemoryKnowledgeRepository()
    existing = build_revision()
    incoming = build_revision(
        statement="Changed statement.",
    )
    repository.save(existing)

    with pytest.raises(
        KnowledgeItemConflictError
    ) as error:
        repository.save(incoming)

    assert error.value.item_id == existing.item.id
    assert error.value.version == 1
    assert error.value.existing_fingerprint == (
        existing.fingerprint
    )
    assert error.value.incoming_fingerprint == (
        incoming.fingerprint
    )
    assert str(error.value) == (
        "knowledge item 'knowledge-a' version 1 "
        "already exists with different content"
    )
    assert repository.get_version(
        existing.item.id,
        1,
    ) is existing


def test_rejects_non_initial_first_revision(
) -> None:
    repository = InMemoryKnowledgeRepository()
    incoming = build_revision(
        version=2,
        day=27,
    )

    with pytest.raises(
        KnowledgeRevisionSequenceError
    ) as error:
        repository.save(incoming)

    assert error.value.item_id == incoming.item.id
    assert error.value.expected_version == 1
    assert error.value.incoming_version == 2
    assert repository.history(
        incoming.item.id
    ) == ()


def test_rejects_skipped_revision() -> None:
    repository = InMemoryKnowledgeRepository()
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
    assert repository.history(first.item.id) == (
        first,
    )


def test_rejects_non_increasing_valid_from(
) -> None:
    repository = InMemoryKnowledgeRepository()
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

    assert repository.history(first.item.id) == (
        first,
    )


def test_rejects_non_knowledge_revision() -> None:
    repository = InMemoryKnowledgeRepository()

    with pytest.raises(
        TypeError,
        match=(
            "revision must be a KnowledgeRevision"
        ),
    ):
        repository.save(
            object(),  # type: ignore[arg-type]
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
    repository = InMemoryKnowledgeRepository()

    with pytest.raises(
        ValueError,
        match="item_id must not be empty",
    ):
        repository.history(item_id)


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
    repository = InMemoryKnowledgeRepository()

    with pytest.raises(
        TypeError,
        match="item_id must be a string",
    ):
        repository.history(
            item_id  # type: ignore[arg-type]
        )


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
    version: object,
    expected_exception: type[Exception],
) -> None:
    repository = InMemoryKnowledgeRepository()

    with pytest.raises(expected_exception):
        repository.get_version(
            "knowledge-a",
            version,  # type: ignore[arg-type]
        )
