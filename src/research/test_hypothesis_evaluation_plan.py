from dataclasses import FrozenInstanceError

import pytest

from src.research.hypothesis_evaluation_plan import (
    HypothesisEvaluationPlan,
)


def build_plan(
    **overrides: object,
) -> HypothesisEvaluationPlan:
    values: dict[str, object] = {
        "version": "hypothesis-evaluation-v1",
        "supported_confidence_threshold": 0.75,
        "partially_supported_confidence_threshold": 0.5,
        "rejected_confidence_threshold": 0.75,
        "minimum_decisive_findings": 2,
    }
    values.update(overrides)

    return HypothesisEvaluationPlan(
        **values
    )  # type: ignore[arg-type]


def test_exposes_predeclared_rules() -> None:
    plan = build_plan(
        version=" hypothesis-evaluation-v1 ",
    )

    assert plan.version == (
        "hypothesis-evaluation-v1"
    )
    assert plan.to_dict() == {
        "schema_version": 1,
        "version": "hypothesis-evaluation-v1",
        "supported_confidence_threshold": 0.75,
        "partially_supported_confidence_threshold": (
            0.5
        ),
        "rejected_confidence_threshold": 0.75,
        "minimum_decisive_findings": 2,
    }


def test_is_immutable() -> None:
    plan = build_plan()

    with pytest.raises(FrozenInstanceError):
        plan.minimum_decisive_findings = 3


@pytest.mark.parametrize(
    ("value", "error_type", "message"),
    (
        (
            object(),
            TypeError,
            "version must be a string",
        ),
        (
            " ",
            ValueError,
            "version must not be empty",
        ),
    ),
)
def test_rejects_invalid_version(
    value: object,
    error_type: type[Exception],
    message: str,
) -> None:
    with pytest.raises(
        error_type,
        match=message,
    ):
        build_plan(version=value)


@pytest.mark.parametrize(
    "field_name",
    (
        "supported_confidence_threshold",
        "partially_supported_confidence_threshold",
        "rejected_confidence_threshold",
    ),
)
@pytest.mark.parametrize(
    ("value", "error_type", "message_suffix"),
    (
        (
            True,
            TypeError,
            "must be a real number",
        ),
        (
            float("nan"),
            ValueError,
            "must be finite",
        ),
        (
            -0.01,
            ValueError,
            "must be between 0 and 1",
        ),
        (
            1.01,
            ValueError,
            "must be between 0 and 1",
        ),
    ),
)
def test_rejects_invalid_threshold(
    field_name: str,
    value: object,
    error_type: type[Exception],
    message_suffix: str,
) -> None:
    with pytest.raises(
        error_type,
        match=(
            f"{field_name} {message_suffix}"
        ),
    ):
        build_plan(
            **{field_name: value},
        )


def test_rejects_partial_threshold_above_supported(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "partially_supported_confidence_threshold "
            "must not exceed "
            "supported_confidence_threshold"
        ),
    ):
        build_plan(
            supported_confidence_threshold=0.7,
            partially_supported_confidence_threshold=(
                0.8
            ),
        )


@pytest.mark.parametrize(
    ("value", "error_type", "message"),
    (
        (
            True,
            TypeError,
            "minimum_decisive_findings must be an integer",
        ),
        (
            1.5,
            TypeError,
            "minimum_decisive_findings must be an integer",
        ),
        (
            0,
            ValueError,
            "minimum_decisive_findings must be at least 1",
        ),
    ),
)
def test_rejects_invalid_minimum_findings(
    value: object,
    error_type: type[Exception],
    message: str,
) -> None:
    with pytest.raises(
        error_type,
        match=message,
    ):
        build_plan(
            minimum_decisive_findings=value,
        )


def test_fingerprint_is_deterministic() -> None:
    first = build_plan()
    second = build_plan()

    assert first.fingerprint == second.fingerprint
    assert len(first.fingerprint) == 64


def test_fingerprint_changes_with_rules() -> None:
    first = build_plan()
    second = build_plan(
        minimum_decisive_findings=3,
    )

    assert first.fingerprint != second.fingerprint