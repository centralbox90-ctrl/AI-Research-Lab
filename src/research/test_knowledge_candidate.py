from dataclasses import FrozenInstanceError

import pytest

from src.research.knowledge_candidate import (
    KnowledgeCandidate,
)


def _candidate(
    **changes: object,
) -> KnowledgeCandidate:
    values: dict[str, object] = {
        "id": "candidate-001",
        "statement": "Momentum persists in trends.",
        "confidence": 0.8,
        "applicability": (
            "trending markets",
            "liquid equity indices",
        ),
        "limitations": (
            "not validated in range-bound markets",
        ),
        "supporting_findings": (
            "finding-002",
            "finding-001",
        ),
        "hypothesis_evaluation_ref": (
            "evaluation-001"
        ),
        "provenance": (
            ("pipeline_version", "knowledge-candidate-v1"),
            ("source", "hypothesis-evaluation"),
        ),
    }
    values.update(changes)

    return KnowledgeCandidate(**values)


def test_candidate_is_immutable_and_normalized() -> None:
    candidate = _candidate(
        id=" candidate-001 ",
        statement=" Momentum persists in trends. ",
        applicability=(
            " liquid equity indices ",
            "trending markets",
        ),
    )

    assert candidate.id == "candidate-001"
    assert candidate.statement == (
        "Momentum persists in trends."
    )
    assert candidate.applicability == (
        "liquid equity indices",
        "trending markets",
    )
    assert candidate.supporting_findings == (
        "finding-001",
        "finding-002",
    )

    with pytest.raises(FrozenInstanceError):
        candidate.confidence = 0.9


def test_candidate_serializes_public_contract() -> None:
    payload = _candidate().to_dict()

    assert payload == {
        "schema_version": 1,
        "id": "candidate-001",
        "statement": "Momentum persists in trends.",
        "confidence": 0.8,
        "applicability": [
            "liquid equity indices",
            "trending markets",
        ],
        "limitations": [
            "not validated in range-bound markets",
        ],
        "supporting_findings": [
            "finding-001",
            "finding-002",
        ],
        "hypothesis_evaluation_ref": (
            "evaluation-001"
        ),
        "provenance": {
            "pipeline_version": (
                "knowledge-candidate-v1"
            ),
            "source": "hypothesis-evaluation",
        },
    }


def test_candidate_fingerprint_is_reproducible() -> None:
    first = _candidate()
    second = _candidate(
        applicability=tuple(
            reversed(
                _candidate().applicability
            )
        ),
        supporting_findings=(
            "finding-001",
            "finding-002",
        ),
        provenance=tuple(
            reversed(
                _candidate().provenance
            )
        ),
    )

    assert first.fingerprint == second.fingerprint


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("applicability", ()),
        ("supporting_findings", ()),
        ("provenance", ()),
    ],
)
def test_candidate_requires_traceable_scope(
    field_name: str,
    value: object,
) -> None:
    with pytest.raises(ValueError):
        _candidate(**{field_name: value})


@pytest.mark.parametrize(
    "confidence",
    [
        -0.1,
        1.1,
        float("nan"),
        True,
        "0.8",
    ],
)
def test_candidate_rejects_invalid_confidence(
    confidence: object,
) -> None:
    with pytest.raises((TypeError, ValueError)):
        _candidate(confidence=confidence)


def test_candidate_rejects_duplicate_references() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "supporting_findings must not "
            "contain duplicates"
        ),
    ):
        _candidate(
            supporting_findings=(
                "finding-001",
                "finding-001",
            )
        )
