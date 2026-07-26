from datetime import datetime, timezone

import pytest

from src.application.in_memory_knowledge_repository import (
    InMemoryKnowledgeRepository,
)
from src.research.knowledge_applicability_query import (
    ApplicabilityMatchMode,
    KnowledgeApplicabilityQuery,
)
from src.research.knowledge_candidate import (
    KnowledgeCandidate,
)
from src.research.knowledge_candidate_validator import (
    KnowledgeCandidateValidator,
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
        items=(left.item, right.item),
        reason=reason,
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


def test_finds_matching_latest_items_in_id_order(
) -> None:
    repository = InMemoryKnowledgeRepository()
    item_b = build_revision(
        item_id="knowledge-b",
        applicability=(
            "liquid markets",
            "trend regime",
        ),
    )
    item_a_v1 = build_revision(
        item_id="knowledge-a",
        applicability=(
            "liquid markets",
            "trend regime",
        ),
    )
    item_a_v2 = build_revision(
        item_id="knowledge-a",
        statement="Updated statement A.",
        version=2,
        day=27,
        applicability=(
            "liquid markets",
            "range regime",
        ),
    )
    item_c = build_revision(
        item_id="knowledge-c",
        applicability=(
            "trend regime",
            "liquid markets",
        ),
    )
    repository.save(item_c)
    repository.save(item_a_v1)
    repository.save(item_b)
    repository.save(item_a_v2)
    query = KnowledgeApplicabilityQuery(
        terms=(
            "TREND REGIME",
            " liquid markets ",
        ),
    )

    assert repository.find_applicable(query) == (
        item_b.item,
        item_c.item,
    )


def test_finds_latest_items_with_any_match_mode(
) -> None:
    repository = InMemoryKnowledgeRepository()
    item_b = build_revision(
        item_id="knowledge-b",
        applicability=("trend regime",),
    )
    item_a = build_revision(
        item_id="knowledge-a",
        applicability=("crisis regime",),
    )
    item_c = build_revision(
        item_id="knowledge-c",
        applicability=("range regime",),
    )
    repository.save(item_c)
    repository.save(item_b)
    repository.save(item_a)
    query = KnowledgeApplicabilityQuery(
        terms=(
            "crisis regime",
            "trend regime",
        ),
        match_mode=ApplicabilityMatchMode.ANY,
    )

    assert repository.find_applicable(query) == (
        item_a.item,
        item_b.item,
    )


def test_find_applicable_returns_empty_tuple(
) -> None:
    repository = InMemoryKnowledgeRepository()
    repository.save(build_revision())
    query = KnowledgeApplicabilityQuery(
        terms=("crisis regime",),
    )

    assert repository.find_applicable(query) == ()


def test_find_applicable_rejects_non_query(
) -> None:
    repository = InMemoryKnowledgeRepository()

    with pytest.raises(
        TypeError,
        match=(
            "query must be a "
            "KnowledgeApplicabilityQuery"
        ),
    ):
        repository.find_applicable(
            object(),  # type: ignore[arg-type]
        )


def test_registers_contradictions_in_item_order(
) -> None:
    repository = InMemoryKnowledgeRepository()
    item_c = build_revision(
        item_id="knowledge-c",
        statement="Statement C.",
    )
    item_b = build_revision(
        item_id="knowledge-b",
        statement="Statement B.",
    )
    item_a = build_revision(
        item_id="knowledge-a",
        statement="Statement A.",
    )
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

    assert repository.list_contradictions() == (
        contradiction_ab,
        contradiction_bc,
    )
    assert repository.contradictions_for(
        " knowledge-b "
    ) == (
        contradiction_ab,
        contradiction_bc,
    )


def test_contradiction_registration_is_idempotent(
) -> None:
    repository = InMemoryKnowledgeRepository()
    left = build_revision(
        item_id="knowledge-a",
        statement="Statement A.",
    )
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

    repository.save_contradiction(contradiction)
    repository.save_contradiction(contradiction)

    assert repository.list_contradictions() == (
        contradiction,
    )


def test_retains_contradiction_for_superseded_item(
) -> None:
    repository = InMemoryKnowledgeRepository()
    left_v1 = build_revision(
        item_id="knowledge-a",
        statement="Statement A.",
    )
    right = build_revision(
        item_id="knowledge-b",
        statement="Statement B.",
    )
    left_v2 = build_revision(
        item_id="knowledge-a",
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
    repository.save_contradiction(contradiction)

    repository.save(left_v2)

    assert repository.get(left_v1.item.id) is (
        left_v2.item
    )
    assert repository.list_contradictions() == (
        contradiction,
    )
    assert contradiction.items[0] is left_v1.item


def test_preserves_distinct_contradiction_reasons(
) -> None:
    repository = InMemoryKnowledgeRepository()
    left = build_revision(
        item_id="knowledge-a",
        statement="Statement A.",
    )
    right = build_revision(
        item_id="knowledge-b",
        statement="Statement B.",
    )
    repository.save(left)
    repository.save(right)
    first = build_contradiction(
        left,
        right,
        reason="First reason.",
    )
    second = build_contradiction(
        left,
        right,
        reason="Second reason.",
    )

    repository.save_contradiction(second)
    repository.save_contradiction(first)

    assert repository.list_contradictions() == (
        first,
        second,
    )


def test_returns_empty_contradictions_for_unknown_item(
) -> None:
    repository = InMemoryKnowledgeRepository()

    assert repository.list_contradictions() == ()
    assert repository.contradictions_for(
        "unknown-item"
    ) == ()


def test_rejects_unstored_contradiction_item(
) -> None:
    repository = InMemoryKnowledgeRepository()
    left = build_revision(
        item_id="knowledge-a",
        statement="Statement A.",
    )
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
) -> None:
    repository = InMemoryKnowledgeRepository()
    stored_left = build_revision(
        item_id="knowledge-a",
        statement="Stored statement A.",
    )
    incoming_left = build_revision(
        item_id="knowledge-a",
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


def test_rejects_non_knowledge_contradiction(
) -> None:
    repository = InMemoryKnowledgeRepository()

    with pytest.raises(
        TypeError,
        match=(
            "contradiction must be a "
            "KnowledgeContradiction"
        ),
    ):
        repository.save_contradiction(
            object(),  # type: ignore[arg-type]
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
