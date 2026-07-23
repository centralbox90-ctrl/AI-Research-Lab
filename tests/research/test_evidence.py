from dataclasses import FrozenInstanceError

import pytest

from src.research.evidence import (
    Evidence,
    EvidenceDirection,
    EvidenceStrength,
)


def build_evidence(
    **overrides: object,
) -> Evidence:
    arguments: dict[str, object] = {
        "id": " evidence-1 ",
        "hypothesis_id": " hypothesis-1 ",
        "observation_refs": (
            "observation-1",
            "observation-2",
        ),
        "direction": EvidenceDirection.SUPPORTING,
        "strength": EvidenceStrength.MODERATE,
        "confidence": 0.8,
        "consistency": 0.75,
        "robustness": 0.6,
        "applicability": (
            "EURUSD",
            "H1",
        ),
        "limitations": (
            "single market",
        ),
        "provenance": (
            (
                "research_fingerprint",
                "research-id",
            ),
            (
                "dataset_id",
                "dataset-id",
            ),
            (
                "evaluation_plan_fingerprint",
                "plan-id",
            ),
        ),
    }
    arguments.update(overrides)

    return Evidence(
        **arguments,  # type: ignore[arg-type]
    )


def test_builds_immutable_evidence() -> None:
    evidence = build_evidence()

    assert evidence.id == "evidence-1"
    assert evidence.hypothesis_id == "hypothesis-1"
    assert evidence.observation_refs == (
        "observation-1",
        "observation-2",
    )
    assert evidence.direction is (
        EvidenceDirection.SUPPORTING
    )
    assert evidence.strength is (
        EvidenceStrength.MODERATE
    )
    assert evidence.confidence == pytest.approx(0.8)
    assert evidence.consistency == pytest.approx(0.75)
    assert evidence.robustness == pytest.approx(0.6)
    assert evidence.applicability == (
        "EURUSD",
        "H1",
    )
    assert evidence.limitations == (
        "single market",
    )
    assert evidence.provenance == (
        (
            "dataset_id",
            "dataset-id",
        ),
        (
            "evaluation_plan_fingerprint",
            "plan-id",
        ),
        (
            "research_fingerprint",
            "research-id",
        ),
    )

    with pytest.raises(FrozenInstanceError):
        evidence.confidence = 0.1


def test_presents_deterministic_payload() -> None:
    evidence = build_evidence()

    assert evidence.to_dict() == {
        "schema_version": 1,
        "id": "evidence-1",
        "hypothesis_id": "hypothesis-1",
        "observation_refs": [
            "observation-1",
            "observation-2",
        ],
        "direction": "supporting",
        "strength": "moderate",
        "confidence": 0.8,
        "consistency": 0.75,
        "robustness": 0.6,
        "applicability": [
            "EURUSD",
            "H1",
        ],
        "limitations": [
            "single market",
        ],
        "provenance": {
            "dataset_id": "dataset-id",
            "evaluation_plan_fingerprint": (
                "plan-id"
            ),
            "research_fingerprint": "research-id",
        },
    }


def test_fingerprint_is_canonical() -> None:
    first = build_evidence(
        provenance=(
            (
                "research_fingerprint",
                "research-id",
            ),
            (
                "dataset_id",
                "dataset-id",
            ),
        )
    )
    second = build_evidence(
        provenance=(
            (
                "dataset_id",
                "dataset-id",
            ),
            (
                "research_fingerprint",
                "research-id",
            ),
        )
    )

    assert first.fingerprint == second.fingerprint
    assert len(first.fingerprint) == 64
    assert first.fingerprint != build_evidence(
        confidence=0.7,
    ).fingerprint


@pytest.mark.parametrize(
    (
        "field_name",
        "invalid_value",
        "error_type",
        "message",
    ),
    [
        (
            "id",
            object(),
            TypeError,
            "id must be a string",
        ),
        (
            "id",
            "   ",
            ValueError,
            "id must not be empty",
        ),
        (
            "hypothesis_id",
            object(),
            TypeError,
            "hypothesis_id must be a string",
        ),
        (
            "hypothesis_id",
            "",
            ValueError,
            "hypothesis_id must not be empty",
        ),
    ],
)
def test_rejects_invalid_identity(
    field_name: str,
    invalid_value: object,
    error_type: type[Exception],
    message: str,
) -> None:
    with pytest.raises(
        error_type,
        match=message,
    ):
        build_evidence(
            **{field_name: invalid_value}
        )


@pytest.mark.parametrize(
    (
        "field_name",
        "invalid_value",
        "error_type",
        "message",
    ),
    [
        (
            "observation_refs",
            [],
            TypeError,
            "observation_refs must be a tuple",
        ),
        (
            "observation_refs",
            (),
            ValueError,
            "observation_refs must not be empty",
        ),
        (
            "observation_refs",
            (
                "observation-1",
                " observation-1 ",
            ),
            ValueError,
            "observation_refs must not contain "
            "duplicates",
        ),
        (
            "observation_refs",
            (
                "",
            ),
            ValueError,
            "observation_refs must not be empty",
        ),
        (
            "applicability",
            [],
            TypeError,
            "applicability must be a tuple",
        ),
        (
            "applicability",
            (
                "EURUSD",
                " EURUSD ",
            ),
            ValueError,
            "applicability must not contain duplicates",
        ),
        (
            "limitations",
            (
                "",
            ),
            ValueError,
            "limitations must not be empty",
        ),
    ],
)
def test_rejects_invalid_text_collection(
    field_name: str,
    invalid_value: object,
    error_type: type[Exception],
    message: str,
) -> None:
    with pytest.raises(
        error_type,
        match=message,
    ):
        build_evidence(
            **{field_name: invalid_value}
        )


@pytest.mark.parametrize(
    (
        "field_name",
        "invalid_value",
        "message",
    ),
    [
        (
            "direction",
            "supporting",
            "direction must be an EvidenceDirection",
        ),
        (
            "strength",
            "strong",
            "strength must be an EvidenceStrength",
        ),
    ],
)
def test_rejects_invalid_enum(
    field_name: str,
    invalid_value: object,
    message: str,
) -> None:
    with pytest.raises(
        TypeError,
        match=message,
    ):
        build_evidence(
            **{field_name: invalid_value}
        )


@pytest.mark.parametrize(
    (
        "field_name",
        "invalid_value",
        "error_type",
        "message",
    ),
    [
        (
            "confidence",
            True,
            TypeError,
            "confidence must be a real number",
        ),
        (
            "confidence",
            float("inf"),
            ValueError,
            "confidence must be finite",
        ),
        (
            "consistency",
            -0.1,
            ValueError,
            "consistency must be between 0 and 1",
        ),
        (
            "robustness",
            1.1,
            ValueError,
            "robustness must be between 0 and 1",
        ),
    ],
)
def test_rejects_invalid_score(
    field_name: str,
    invalid_value: object,
    error_type: type[Exception],
    message: str,
) -> None:
    with pytest.raises(
        error_type,
        match=message,
    ):
        build_evidence(
            **{field_name: invalid_value}
        )


@pytest.mark.parametrize(
    (
        "invalid_value",
        "error_type",
        "message",
    ),
    [
        (
            [],
            TypeError,
            "provenance must be a tuple",
        ),
        (
            (),
            ValueError,
            "provenance must not be empty",
        ),
        (
            (
                ("key",),
            ),
            TypeError,
            "each provenance entry must be "
            "a key-value tuple",
        ),
        (
            (
                ("key", "value"),
                (" key ", "other"),
            ),
            ValueError,
            "provenance keys must be unique",
        ),
        (
            (
                ("", "value"),
            ),
            ValueError,
            "provenance key must not be empty",
        ),
        (
            (
                ("key", ""),
            ),
            ValueError,
            "provenance value must not be empty",
        ),
    ],
)
def test_rejects_invalid_provenance(
    invalid_value: object,
    error_type: type[Exception],
    message: str,
) -> None:
    with pytest.raises(
        error_type,
        match=message,
    ):
        build_evidence(
            provenance=invalid_value,
        )
