import pytest

from src.research.knowledge_candidate import (
    KnowledgeCandidate,
)
from src.research.knowledge_candidate_validator import (
    KnowledgeCandidateValidationError,
    KnowledgeCandidateValidator,
)
from src.research.knowledge_item import KnowledgeItem


def build_candidate(
    *,
    confidence: float = 0.85,
    supporting_findings: tuple[str, ...] = (
        "finding-a",
        "finding-b",
    ),
    provenance: tuple[
        tuple[str, str],
        ...,
    ] = (
        ("dataset_fingerprint", "dataset-123"),
    ),
) -> KnowledgeCandidate:
    return KnowledgeCandidate(
        id="candidate-momentum",
        statement=(
            "Momentum persists in liquid trend regimes."
        ),
        confidence=confidence,
        applicability=(
            "liquid equity indices",
            "persistent trends",
        ),
        limitations=(
            "not evaluated in crisis regimes",
        ),
        supporting_findings=supporting_findings,
        hypothesis_evaluation_ref=(
            "hypothesis-evaluation-123"
        ),
        provenance=provenance,
    )


def build_validator(
    *,
    minimum_confidence: float = 0.75,
    minimum_supporting_findings: int = 2,
) -> KnowledgeCandidateValidator:
    return KnowledgeCandidateValidator(
        minimum_confidence=minimum_confidence,
        minimum_supporting_findings=(
            minimum_supporting_findings
        ),
    )


def test_accepts_candidate_as_initial_knowledge_item(
) -> None:
    candidate = build_candidate()

    item = build_validator().validate(
        candidate=candidate
    )

    assert isinstance(item, KnowledgeItem)
    assert item.id == candidate.id
    assert item.statement == candidate.statement
    assert item.confidence == candidate.confidence
    assert item.applicability == (
        candidate.applicability
    )
    assert item.limitations == candidate.limitations
    assert item.supporting_findings == (
        candidate.supporting_findings
    )
    assert item.version == 1

    provenance = dict(item.provenance)

    assert provenance["dataset_fingerprint"] == (
        "dataset-123"
    )
    assert provenance[
        "hypothesis_evaluation_ref"
    ] == candidate.hypothesis_evaluation_ref
    assert provenance[
        "knowledge_candidate_id"
    ] == candidate.id
    assert provenance[
        "knowledge_candidate_fingerprint"
    ] == candidate.fingerprint
    assert provenance[
        "knowledge_validation_minimum_confidence"
    ] == "0.75"
    assert provenance[
        "knowledge_validation_minimum_supporting_findings"
    ] == "2"
    assert provenance[
        "knowledge_validation_policy_version"
    ] == "1"


def test_validation_is_deterministic() -> None:
    candidate = build_candidate()
    validator = build_validator()

    first = validator.validate(
        candidate=candidate
    )
    second = validator.validate(
        candidate=candidate
    )

    assert first == second
    assert first.fingerprint == second.fingerprint


def test_authoritative_traceability_overrides_spoofed_values(
) -> None:
    candidate = build_candidate(
        provenance=(
            (
                "knowledge_candidate_id",
                "spoofed-id",
            ),
            (
                "knowledge_candidate_fingerprint",
                "spoofed-fingerprint",
            ),
            (
                "hypothesis_evaluation_ref",
                "spoofed-evaluation",
            ),
        ),
    )

    item = build_validator().validate(
        candidate=candidate
    )
    provenance = dict(item.provenance)

    assert provenance[
        "knowledge_candidate_id"
    ] == candidate.id
    assert provenance[
        "knowledge_candidate_fingerprint"
    ] == candidate.fingerprint
    assert provenance[
        "hypothesis_evaluation_ref"
    ] == candidate.hypothesis_evaluation_ref


def test_accepts_values_at_policy_boundaries() -> None:
    candidate = build_candidate(
        confidence=0.75,
    )

    item = build_validator().validate(
        candidate=candidate
    )

    assert item.confidence == pytest.approx(0.75)


def test_rejects_low_confidence() -> None:
    candidate = build_candidate(
        confidence=0.74,
    )

    with pytest.raises(
        KnowledgeCandidateValidationError
    ) as error:
        build_validator().validate(
            candidate=candidate
        )

    assert error.value.candidate_id == candidate.id
    assert error.value.reasons == (
        "confidence must be at least 0.75",
    )


def test_rejects_insufficient_supporting_findings(
) -> None:
    candidate = build_candidate(
        supporting_findings=(
            "finding-a",
        ),
    )

    with pytest.raises(
        KnowledgeCandidateValidationError
    ) as error:
        build_validator().validate(
            candidate=candidate
        )

    assert error.value.reasons == (
        "supporting_findings must contain "
        "at least 2 items",
    )


def test_reports_all_rejection_reasons_in_stable_order(
) -> None:
    candidate = build_candidate(
        confidence=0.2,
        supporting_findings=(
            "finding-a",
        ),
    )

    with pytest.raises(
        KnowledgeCandidateValidationError
    ) as error:
        build_validator().validate(
            candidate=candidate
        )

    assert error.value.reasons == (
        "confidence must be at least 0.75",
        "supporting_findings must contain "
        "at least 2 items",
    )
    assert str(error.value) == (
        "knowledge candidate "
        "'candidate-momentum' was rejected: "
        "confidence must be at least 0.75; "
        "supporting_findings must contain "
        "at least 2 items"
    )


def test_rejects_non_candidate_input() -> None:
    with pytest.raises(
        TypeError,
        match="candidate must be a KnowledgeCandidate",
    ):
        build_validator().validate(
            candidate=object(),  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    ("value", "expected_exception"),
    (
        (True, TypeError),
        ("0.75", TypeError),
        (float("nan"), ValueError),
        (float("inf"), ValueError),
        (-0.1, ValueError),
        (1.1, ValueError),
    ),
)
def test_rejects_invalid_minimum_confidence(
    value: object,
    expected_exception: type[Exception],
) -> None:
    with pytest.raises(expected_exception):
        KnowledgeCandidateValidator(
            minimum_confidence=value,  # type: ignore[arg-type]
            minimum_supporting_findings=2,
        )


@pytest.mark.parametrize(
    ("value", "expected_exception"),
    (
        (True, TypeError),
        (1.5, TypeError),
        ("2", TypeError),
        (0, ValueError),
        (-1, ValueError),
    ),
)
def test_rejects_invalid_minimum_supporting_findings(
    value: object,
    expected_exception: type[Exception],
) -> None:
    with pytest.raises(expected_exception):
        KnowledgeCandidateValidator(
            minimum_confidence=0.75,
            minimum_supporting_findings=value,  # type: ignore[arg-type]
        )
