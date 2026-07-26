from dataclasses import FrozenInstanceError

import pytest

from src.research.knowledge_item import (
    KnowledgeItem,
)


def _item(
    **changes: object,
) -> KnowledgeItem:
    values: dict[str, object] = {
        "id": "knowledge-001",
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
        "version": 1,
        "provenance": (
            ("candidate_fingerprint", "candidate-sha256"),
            ("validation_version", "knowledge-validation-v1"),
        ),
    }
    values.update(changes)

    return KnowledgeItem(**values)


def test_item_is_immutable_and_normalized() -> None:
    item = _item(
        id=" knowledge-001 ",
        statement=" Momentum persists in trends. ",
        applicability=(
            " liquid equity indices ",
            "trending markets",
        ),
    )

    assert item.id == "knowledge-001"
    assert item.statement == (
        "Momentum persists in trends."
    )
    assert item.applicability == (
        "liquid equity indices",
        "trending markets",
    )
    assert item.supporting_findings == (
        "finding-001",
        "finding-002",
    )
    assert item.version == 1

    with pytest.raises(FrozenInstanceError):
        item.version = 2


def test_item_serializes_public_contract() -> None:
    payload = _item().to_dict()

    assert payload == {
        "schema_version": 1,
        "id": "knowledge-001",
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
        "version": 1,
        "provenance": {
            "candidate_fingerprint": "candidate-sha256",
            "validation_version": (
                "knowledge-validation-v1"
            ),
        },
    }


def test_item_fingerprint_is_reproducible() -> None:
    first = _item()
    second = _item(
        applicability=tuple(
            reversed(
                _item().applicability
            )
        ),
        supporting_findings=(
            "finding-001",
            "finding-002",
        ),
        provenance=tuple(
            reversed(
                _item().provenance
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
def test_item_requires_traceable_scope(
    field_name: str,
    value: object,
) -> None:
    with pytest.raises(ValueError):
        _item(**{field_name: value})


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
def test_item_rejects_invalid_confidence(
    confidence: object,
) -> None:
    with pytest.raises((TypeError, ValueError)):
        _item(confidence=confidence)


@pytest.mark.parametrize(
    "version",
    [
        0,
        -1,
        1.0,
        True,
    ],
)
def test_item_requires_positive_integer_version(
    version: object,
) -> None:
    with pytest.raises((TypeError, ValueError)):
        _item(version=version)


def test_item_rejects_duplicate_references() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "supporting_findings must not "
            "contain duplicates"
        ),
    ):
        _item(
            supporting_findings=(
                "finding-001",
                "finding-001",
            )
        )
