from datetime import datetime, timezone

import pytest

from src.application.in_memory_knowledge_repository import (
    InMemoryKnowledgeRepository,
)
from src.research.knowledge_applicability_query import (
    KnowledgeApplicabilityQuery,
)
from src.research.knowledge_contradiction_detector import (
    KnowledgeContradictionDetector,
)
from src.research.knowledge_contradiction_rule import (
    KnowledgeContradictionRule,
)
from src.research.knowledge_item import KnowledgeItem
from src.research.knowledge_revision import (
    KnowledgeRevision,
)


def build_item(
    *,
    item_id: str,
    statement: str,
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
    *,
    item_id: str,
    statement: str,
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


def build_rule(
    left: str,
    right: str,
    reason: str,
) -> KnowledgeContradictionRule:
    return KnowledgeContradictionRule(
        statements=(left, right),
        reason=reason,
    )


def test_detects_conflicts_in_deterministic_item_order(
) -> None:
    repository = InMemoryKnowledgeRepository()
    item_c = build_revision(
        item_id="knowledge-c",
        statement="Volatility clusters.",
    )
    item_b = build_revision(
        item_id="knowledge-b",
        statement="Momentum does not persist.",
    )
    item_a = build_revision(
        item_id="knowledge-a",
        statement="Momentum persists.",
    )
    repository.save(item_c)
    repository.save(item_b)
    repository.save(item_a)
    rules = (
        build_rule(
            "Momentum does not persist.",
            "Volatility clusters.",
            "Dependent conclusions conflict.",
        ),
        build_rule(
            "Momentum persists.",
            "Momentum does not persist.",
            "Opposing momentum conclusions.",
        ),
    )

    contradictions = (
        KnowledgeContradictionDetector().detect(
            repository=repository,
            rules=rules,
        )
    )

    assert tuple(
        tuple(item.id for item in result.items)
        for result in contradictions
    ) == (
        ("knowledge-a", "knowledge-b"),
        ("knowledge-b", "knowledge-c"),
    )
    assert tuple(
        result.reason
        for result in contradictions
    ) == (
        "Opposing momentum conclusions.",
        "Dependent conclusions conflict.",
    )
    assert all(
        result.conflicting_applicability
        == ("liquid markets",)
        for result in contradictions
    )


def test_result_is_independent_of_rule_order(
) -> None:
    repository = InMemoryKnowledgeRepository()
    repository.save(
        build_revision(
            item_id="knowledge-b",
            statement="Momentum does not persist.",
        )
    )
    repository.save(
        build_revision(
            item_id="knowledge-a",
            statement="Momentum persists.",
        )
    )
    first_rule = build_rule(
        "Momentum persists.",
        "Momentum does not persist.",
        "Opposing momentum conclusions.",
    )
    unrelated_rule = build_rule(
        "Volatility clusters.",
        "Volatility does not cluster.",
        "Opposing volatility conclusions.",
    )
    detector = KnowledgeContradictionDetector()

    first = detector.detect(
        repository=repository,
        rules=(first_rule, unrelated_rule),
    )
    second = detector.detect(
        repository=repository,
        rules=(unrelated_rule, first_rule),
    )

    assert first == second
    assert tuple(
        item.fingerprint
        for item in first
    ) == tuple(
        item.fingerprint
        for item in second
    )


def test_uses_only_latest_repository_items(
) -> None:
    repository = InMemoryKnowledgeRepository()
    positive_v1 = build_revision(
        item_id="knowledge-positive",
        statement="Momentum persists.",
    )
    positive_v2 = build_revision(
        item_id="knowledge-positive",
        statement="Momentum is regime dependent.",
        version=2,
        day=27,
    )
    negative = build_revision(
        item_id="knowledge-negative",
        statement="Momentum does not persist.",
    )
    repository.save(positive_v1)
    repository.save(positive_v2)
    repository.save(negative)
    rule = build_rule(
        "Momentum persists.",
        "Momentum does not persist.",
        "Opposing momentum conclusions.",
    )

    contradictions = (
        KnowledgeContradictionDetector().detect(
            repository=repository,
            rules=(rule,),
        )
    )

    assert contradictions == ()


def test_requires_overlapping_applicability(
) -> None:
    repository = InMemoryKnowledgeRepository()
    repository.save(
        build_revision(
            item_id="knowledge-positive",
            statement="Momentum persists.",
            applicability=("trend regime",),
        )
    )
    repository.save(
        build_revision(
            item_id="knowledge-negative",
            statement="Momentum does not persist.",
            applicability=("range regime",),
        )
    )
    rule = build_rule(
        "Momentum persists.",
        "Momentum does not persist.",
        "Opposing momentum conclusions.",
    )

    contradictions = (
        KnowledgeContradictionDetector().detect(
            repository=repository,
            rules=(rule,),
        )
    )

    assert contradictions == ()


def test_returns_empty_tuple_without_matching_rule(
) -> None:
    repository = InMemoryKnowledgeRepository()
    repository.save(
        build_revision(
            item_id="knowledge-a",
            statement="Momentum persists.",
        )
    )
    repository.save(
        build_revision(
            item_id="knowledge-b",
            statement="Volatility clusters.",
        )
    )
    rule = build_rule(
        "Momentum persists.",
        "Momentum does not persist.",
        "Opposing momentum conclusions.",
    )

    assert (
        KnowledgeContradictionDetector().detect(
            repository=repository,
            rules=(rule,),
        )
        == ()
    )


def test_accepts_empty_rules() -> None:
    repository = InMemoryKnowledgeRepository()
    repository.save(
        build_revision(
            item_id="knowledge-a",
            statement="Momentum persists.",
        )
    )

    assert (
        KnowledgeContradictionDetector().detect(
            repository=repository,
            rules=(),
        )
        == ()
    )


def test_rejects_non_repository() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "repository must implement "
            "KnowledgeRepository"
        ),
    ):
        KnowledgeContradictionDetector().detect(
            repository=object(),  # type: ignore[arg-type]
            rules=(),
        )


@pytest.mark.parametrize(
    "rules",
    (
        [],
        {
            build_rule(
                "Statement A.",
                "Statement B.",
                "Opposing conclusions.",
            ),
        },
    ),
)
def test_rejects_non_tuple_rules(
    rules: object,
) -> None:
    repository = InMemoryKnowledgeRepository()

    with pytest.raises(
        TypeError,
        match="rules must be a tuple",
    ):
        KnowledgeContradictionDetector().detect(
            repository=repository,
            rules=rules,  # type: ignore[arg-type]
        )


def test_rejects_non_rule() -> None:
    repository = InMemoryKnowledgeRepository()

    with pytest.raises(
        TypeError,
        match=(
            "each rule must be a "
            "KnowledgeContradictionRule"
        ),
    ):
        KnowledgeContradictionDetector().detect(
            repository=repository,
            rules=(object(),),  # type: ignore[arg-type]
        )


def test_rejects_duplicate_statement_pairs(
) -> None:
    repository = InMemoryKnowledgeRepository()
    first = build_rule(
        "Statement A.",
        "Statement B.",
        "First reason.",
    )
    second = build_rule(
        " statement b. ",
        "STATEMENT A.",
        "Second reason.",
    )

    with pytest.raises(
        ValueError,
        match=(
            "rules must not contain duplicate "
            "statement pairs"
        ),
    ):
        KnowledgeContradictionDetector().detect(
            repository=repository,
            rules=(first, second),
        )


class RepositoryStub:
    def __init__(
        self,
        items: object,
    ) -> None:
        self.items = items

    def save(self, revision: object) -> None:
        raise NotImplementedError

    def get(self, item_id: str) -> None:
        return None

    def get_version(
        self,
        item_id: str,
        version: int,
    ) -> None:
        return None

    def history(
        self,
        item_id: str,
    ) -> tuple[object, ...]:
        return ()

    def list_all(self) -> object:
        return self.items

    def find_applicable(
        self,
        query: KnowledgeApplicabilityQuery,
    ) -> tuple[KnowledgeItem, ...]:
        return ()

    def save_contradiction(
        self,
        contradiction: object,
    ) -> None:
        raise NotImplementedError

    def list_contradictions(
        self,
    ) -> tuple[object, ...]:
        return ()

    def contradictions_for(
        self,
        item_id: str,
    ) -> tuple[object, ...]:
        return ()


def test_rejects_non_tuple_repository_result(
) -> None:
    repository = RepositoryStub([])

    with pytest.raises(
        TypeError,
        match=(
            "repository list_all must return a tuple"
        ),
    ):
        KnowledgeContradictionDetector().detect(
            repository=repository,  # type: ignore[arg-type]
            rules=(),
        )


def test_rejects_non_knowledge_repository_item(
) -> None:
    repository = RepositoryStub((object(),))

    with pytest.raises(
        TypeError,
        match=(
            "repository items must be "
            "KnowledgeItem objects"
        ),
    ):
        KnowledgeContradictionDetector().detect(
            repository=repository,  # type: ignore[arg-type]
            rules=(),
        )


def test_rejects_duplicate_repository_item_ids(
) -> None:
    first = build_item(
        item_id="knowledge-a",
        statement="Statement A.",
        version=1,
    )
    second = build_item(
        item_id="knowledge-a",
        statement="Updated statement A.",
        version=2,
    )
    repository = RepositoryStub((first, second))

    with pytest.raises(
        ValueError,
        match=(
            "repository must return at most one "
            "version per knowledge ID"
        ),
    ):
        KnowledgeContradictionDetector().detect(
            repository=repository,  # type: ignore[arg-type]
            rules=(),
        )
