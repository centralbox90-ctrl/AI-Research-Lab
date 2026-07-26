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
    repository = InMemoryKnowledgeRepository()

    repository.save(item)

    assert repository.get(item.id) is item
    assert dict(item.provenance)[
        "knowledge_candidate_fingerprint"
    ] == candidate.fingerprint


def test_saves_and_returns_knowledge_item() -> None:
    repository = InMemoryKnowledgeRepository()
    item = build_item()

    repository.save(item)

    assert repository.get(item.id) is item
    assert repository.get(f"  {item.id}  ") is item


def test_returns_none_for_unknown_item() -> None:
    repository = InMemoryKnowledgeRepository()

    assert repository.get("unknown-item") is None


def test_lists_items_in_deterministic_id_order(
) -> None:
    repository = InMemoryKnowledgeRepository()
    item_b = build_item(
        item_id="knowledge-b",
        statement="Statement B.",
    )
    item_a = build_item(
        item_id="knowledge-a",
        statement="Statement A.",
    )

    repository.save(item_b)
    repository.save(item_a)

    assert repository.list_all() == (
        item_a,
        item_b,
    )


def test_repeated_save_of_same_item_is_idempotent(
) -> None:
    repository = InMemoryKnowledgeRepository()
    item = build_item()

    repository.save(item)
    repository.save(item)

    assert repository.list_all() == (item,)


def test_rejects_conflicting_content_for_existing_id(
) -> None:
    repository = InMemoryKnowledgeRepository()
    existing = build_item()
    incoming = build_item(
        statement="Changed statement.",
        version=2,
    )
    repository.save(existing)

    with pytest.raises(
        KnowledgeItemConflictError
    ) as error:
        repository.save(incoming)

    assert error.value.item_id == existing.id
    assert error.value.existing_fingerprint == (
        existing.fingerprint
    )
    assert error.value.incoming_fingerprint == (
        incoming.fingerprint
    )
    assert str(error.value) == (
        "knowledge item 'knowledge-a' already "
        "exists with different content"
    )
    assert repository.get(existing.id) is existing


def test_rejects_non_knowledge_item() -> None:
    repository = InMemoryKnowledgeRepository()

    with pytest.raises(
        TypeError,
        match="item must be a KnowledgeItem",
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
        repository.get(item_id)


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
        repository.get(
            item_id  # type: ignore[arg-type]
        )
