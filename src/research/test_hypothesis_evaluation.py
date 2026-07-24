from dataclasses import FrozenInstanceError

import pytest

from src.research.hypothesis_evaluation import (
    HypothesisEvaluation,
    HypothesisEvaluationState,
)


def build_evaluation(
    **overrides: object,
) -> HypothesisEvaluation:
    values: dict[str, object] = {
        "id": " evaluation-id ",
        "hypothesis_id": " hypothesis-id ",
        "state": (
            HypothesisEvaluationState.SUPPORTED
        ),
        "confidence": 0.8,
        "finding_refs": (
            "finding-b",
            "finding-a",
        ),
        "rationale": (
            "replicated across markets",
            "strong supporting evidence",
        ),
        "limitations": (
            "limited history",
        ),
        "provenance": (
            (
                "evaluation_policy_version",
                "hypothesis-evaluation-v1",
            ),
            (
                "finding_set_fingerprint",
                "finding-set-id",
            ),
        ),
    }
    values.update(overrides)

    return HypothesisEvaluation(**values)


def test_normalizes_and_serializes_evaluation(
) -> None:
    evaluation = build_evaluation()

    assert evaluation.id == "evaluation-id"
    assert evaluation.hypothesis_id == (
        "hypothesis-id"
    )
    assert evaluation.finding_refs == (
        "finding-a",
        "finding-b",
    )
    assert evaluation.rationale == (
        "replicated across markets",
        "strong supporting evidence",
    )

    assert evaluation.to_dict() == {
        "schema_version": 1,
        "id": "evaluation-id",
        "hypothesis_id": "hypothesis-id",
        "state": "supported",
        "confidence": 0.8,
        "finding_refs": [
            "finding-a",
            "finding-b",
        ],
        "rationale": [
            "replicated across markets",
            "strong supporting evidence",
        ],
        "limitations": [
            "limited history",
        ],
        "provenance": {
            "evaluation_policy_version": (
                "hypothesis-evaluation-v1"
            ),
            "finding_set_fingerprint": (
                "finding-set-id"
            ),
        },
    }


@pytest.mark.parametrize(
    "state",
    tuple(HypothesisEvaluationState),
)
def test_accepts_every_architecture_state(
    state: HypothesisEvaluationState,
) -> None:
    evaluation = build_evaluation(
        state=state,
    )

    assert evaluation.state is state


def test_is_immutable() -> None:
    evaluation = build_evaluation()

    with pytest.raises(FrozenInstanceError):
        evaluation.confidence = 0.1


def test_rejects_string_state() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "state must be a "
            "HypothesisEvaluationState"
        ),
    ):
        build_evaluation(
            state="supported",
        )


@pytest.mark.parametrize(
    "confidence",
    (
        -0.01,
        1.01,
        float("inf"),
        float("nan"),
    ),
)
def test_rejects_invalid_confidence(
    confidence: float,
) -> None:
    with pytest.raises(ValueError):
        build_evaluation(
            confidence=confidence,
        )


def test_rejects_boolean_confidence() -> None:
    with pytest.raises(
        TypeError,
        match="confidence must be a real number",
    ):
        build_evaluation(
            confidence=True,
        )


@pytest.mark.parametrize(
    ("field_name", "value"),
    (
        ("finding_refs", ()),
        ("rationale", ()),
        ("provenance", ()),
    ),
)
def test_requires_scientific_basis(
    field_name: str,
    value: tuple[object, ...],
) -> None:
    with pytest.raises(
        ValueError,
        match=f"{field_name} must not be empty",
    ):
        build_evaluation(
            **{field_name: value},
        )


@pytest.mark.parametrize(
    "field_name",
    (
        "finding_refs",
        "rationale",
        "limitations",
    ),
)
def test_rejects_duplicate_items(
    field_name: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            f"{field_name} must not "
            "contain duplicates"
        ),
    ):
        build_evaluation(
            **{
                field_name: (
                    "duplicate",
                    " duplicate ",
                )
            },
        )


def test_fingerprint_is_deterministic() -> None:
    first = build_evaluation()
    second = build_evaluation()

    assert first.fingerprint == second.fingerprint
    assert len(first.fingerprint) == 64


def test_fingerprint_changes_with_state() -> None:
    supported = build_evaluation()
    rejected = build_evaluation(
        state=HypothesisEvaluationState.REJECTED,
    )

    assert supported.fingerprint != (
        rejected.fingerprint
    )