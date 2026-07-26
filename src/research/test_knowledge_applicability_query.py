from dataclasses import FrozenInstanceError

import pytest

from src.research.knowledge_applicability_query import (
    ApplicabilityMatchMode,
    KnowledgeApplicabilityQuery,
)
from src.research.knowledge_item import KnowledgeItem


def build_item(
    *,
    applicability: tuple[str, ...] = (
        "Daily",
        "Liquid Equity Indices",
        "Trending Markets",
    ),
) -> KnowledgeItem:
    return KnowledgeItem(
        id="knowledge-momentum",
        statement=(
            "Momentum persists in liquid trend regimes."
        ),
        confidence=0.85,
        applicability=applicability,
        limitations=(
            "not evaluated in crisis regimes",
        ),
        supporting_findings=(
            "finding-a",
            "finding-b",
        ),
        version=1,
        provenance=(
            (
                "knowledge_candidate_id",
                "candidate-momentum",
            ),
        ),
    )


def test_normalizes_terms_for_all_match() -> None:
    query = KnowledgeApplicabilityQuery(
        terms=(
            " Trending Markets ",
            "DAILY",
        ),
    )

    assert query.terms == (
        "daily",
        "trending markets",
    )
    assert query.match_mode is (
        ApplicabilityMatchMode.ALL
    )


def test_all_mode_matches_every_required_term(
) -> None:
    query = KnowledgeApplicabilityQuery(
        terms=(
            "daily",
            "LIQUID EQUITY INDICES",
        ),
    )

    assert query.matches(build_item()) is True


def test_all_mode_rejects_missing_term() -> None:
    query = KnowledgeApplicabilityQuery(
        terms=(
            "daily",
            "crypto",
        ),
    )

    assert query.matches(build_item()) is False


def test_any_mode_matches_one_term() -> None:
    query = KnowledgeApplicabilityQuery(
        terms=(
            "crypto",
            "trending markets",
        ),
        match_mode=ApplicabilityMatchMode.ANY,
    )

    assert query.matches(build_item()) is True


def test_any_mode_rejects_when_no_term_matches(
) -> None:
    query = KnowledgeApplicabilityQuery(
        terms=(
            "crypto",
            "weekly",
        ),
        match_mode=ApplicabilityMatchMode.ANY,
    )

    assert query.matches(build_item()) is False


def test_serializes_normalized_query() -> None:
    query = KnowledgeApplicabilityQuery(
        terms=(
            "Daily",
            "Trending Markets",
        ),
        match_mode=ApplicabilityMatchMode.ANY,
    )

    assert query.to_dict() == {
        "schema_version": 1,
        "terms": [
            "daily",
            "trending markets",
        ],
        "match_mode": "any",
    }


def test_fingerprint_is_order_and_case_deterministic(
) -> None:
    first = KnowledgeApplicabilityQuery(
        terms=(
            "Daily",
            "Trending Markets",
        ),
    )
    second = KnowledgeApplicabilityQuery(
        terms=(
            "trending markets",
            "DAILY",
        ),
    )

    assert first == second
    assert first.fingerprint == second.fingerprint
    assert len(first.fingerprint) == 64


def test_query_is_immutable() -> None:
    query = KnowledgeApplicabilityQuery(
        terms=("daily",),
    )

    with pytest.raises(FrozenInstanceError):
        query.terms = (  # type: ignore[misc]
            "weekly",
        )


def test_rejects_non_knowledge_item() -> None:
    query = KnowledgeApplicabilityQuery(
        terms=("daily",),
    )

    with pytest.raises(
        TypeError,
        match="item must be a KnowledgeItem",
    ):
        query.matches(
            object()  # type: ignore[arg-type]
        )


def test_rejects_non_tuple_terms() -> None:
    with pytest.raises(
        TypeError,
        match="terms must be a tuple",
    ):
        KnowledgeApplicabilityQuery(
            terms=["daily"],  # type: ignore[arg-type]
        )


def test_rejects_empty_terms() -> None:
    with pytest.raises(
        ValueError,
        match="terms must not be empty",
    ):
        KnowledgeApplicabilityQuery(terms=())


def test_rejects_non_string_term() -> None:
    with pytest.raises(
        TypeError,
        match="each term must be a string",
    ):
        KnowledgeApplicabilityQuery(
            terms=(1,),  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "term",
    (
        "",
        "   ",
    ),
)
def test_rejects_empty_term(
    term: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "terms must not contain empty values"
        ),
    ):
        KnowledgeApplicabilityQuery(
            terms=(term,),
        )


def test_rejects_case_insensitive_duplicates(
) -> None:
    with pytest.raises(
        ValueError,
        match="terms must not contain duplicates",
    ):
        KnowledgeApplicabilityQuery(
            terms=(
                "Daily",
                " daily ",
            ),
        )


@pytest.mark.parametrize(
    "match_mode",
    (
        "all",
        None,
        object(),
    ),
)
def test_rejects_invalid_match_mode(
    match_mode: object,
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "match_mode must be an "
            "ApplicabilityMatchMode"
        ),
    ):
        KnowledgeApplicabilityQuery(
            terms=("daily",),
            match_mode=match_mode,  # type: ignore[arg-type]
        )
