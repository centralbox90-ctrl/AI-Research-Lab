from dataclasses import FrozenInstanceError

import pytest

from src.research.comparative_evaluation_plan import (
    ComparativeEvaluationPlan,
    ExpectedEffectDirection,
)


def build_plan(
    **overrides: object,
) -> ComparativeEvaluationPlan:
    arguments: dict[str, object] = {
        "expected_direction": (
            ExpectedEffectDirection.POSITIVE
        ),
        "method": "moving_block_bootstrap",
        "confidence_level": 0.95,
        "resample_count": 2_000,
        "block_length": 24,
        "random_seed": 0,
        "minimum_candidate_sample_size": 30,
        "minimum_replication_count": 2,
        "minimum_supporting_replication_count": 2,
    }
    arguments.update(overrides)

    return ComparativeEvaluationPlan(
        **arguments,  # type: ignore[arg-type]
    )


def test_builds_default_predeclared_plan(
) -> None:
    plan = ComparativeEvaluationPlan()

    assert plan.expected_direction is (
        ExpectedEffectDirection.POSITIVE
    )
    assert plan.method == "moving_block_bootstrap"
    assert plan.confidence_level == 0.95
    assert plan.resample_count == 2_000
    assert plan.block_length == 24
    assert plan.random_seed == 0
    assert plan.minimum_candidate_sample_size == 30
    assert plan.minimum_replication_count == 2
    assert (
        plan.minimum_supporting_replication_count
        == 2
    )


def test_normalizes_method_and_is_immutable(
) -> None:
    plan = build_plan(
        method="  moving_block_bootstrap  ",
    )

    assert plan.method == "moving_block_bootstrap"

    with pytest.raises(FrozenInstanceError):
        setattr(plan, "block_length", 48)


@pytest.mark.parametrize(
    "direction",
    tuple(ExpectedEffectDirection),
)
def test_accepts_each_expected_direction(
    direction: ExpectedEffectDirection,
) -> None:
    plan = build_plan(
        expected_direction=direction,
    )

    assert plan.expected_direction is direction
    assert plan.to_dict()[
        "expected_direction"
    ] == direction.value


def test_serializes_complete_plan() -> None:
    plan = build_plan()

    assert plan.to_dict() == {
        "schema_version": 1,
        "expected_direction": "positive",
        "method": "moving_block_bootstrap",
        "confidence_level": 0.95,
        "resample_count": 2_000,
        "block_length": 24,
        "random_seed": 0,
        "minimum_candidate_sample_size": 30,
        "minimum_replication_count": 2,
        "minimum_supporting_replication_count": 2,
    }


def test_fingerprint_is_deterministic(
) -> None:
    first = build_plan()
    second = build_plan()
    changed = build_plan(
        block_length=48,
    )

    assert first.fingerprint == second.fingerprint
    assert first.fingerprint != changed.fingerprint
    assert len(first.fingerprint) == 64
    assert int(first.fingerprint, 16) >= 0


@pytest.mark.parametrize(
    "field_name",
    [
        "confidence_level",
        "resample_count",
        "block_length",
        "random_seed",
        "minimum_candidate_sample_size",
        "minimum_replication_count",
        "minimum_supporting_replication_count",
        "expected_direction",
    ],
)
def test_each_field_affects_fingerprint(
    field_name: str,
) -> None:
    changed_values: dict[str, object] = {
        "confidence_level": 0.90,
        "resample_count": 1_000,
        "block_length": 12,
        "random_seed": 17,
        "minimum_candidate_sample_size": 50,
        "minimum_replication_count": 3,
        "minimum_supporting_replication_count": 1,
        "expected_direction": (
            ExpectedEffectDirection.NEGATIVE
        ),
    }

    assert build_plan().fingerprint != (
        build_plan(
            **{
                field_name: changed_values[
                    field_name
                ],
            }
        ).fingerprint
    )


@pytest.mark.parametrize(
    (
        "value",
        "error_type",
        "message",
    ),
    [
        (
            "positive",
            TypeError,
            "expected_direction must be an "
            "ExpectedEffectDirection",
        ),
        (
            object(),
            TypeError,
            "expected_direction must be an "
            "ExpectedEffectDirection",
        ),
    ],
)
def test_rejects_invalid_expected_direction(
    value: object,
    error_type: type[Exception],
    message: str,
) -> None:
    with pytest.raises(
        error_type,
        match=message,
    ):
        build_plan(
            expected_direction=value,
        )


@pytest.mark.parametrize(
    (
        "value",
        "error_type",
        "message",
    ),
    [
        (
            None,
            TypeError,
            "method must be a string",
        ),
        (
            " ",
            ValueError,
            "method must not be empty",
        ),
    ],
)
def test_rejects_invalid_method(
    value: object,
    error_type: type[Exception],
    message: str,
) -> None:
    with pytest.raises(
        error_type,
        match=message,
    ):
        build_plan(
            method=value,
        )


@pytest.mark.parametrize(
    (
        "value",
        "error_type",
        "message",
    ),
    [
        (
            True,
            TypeError,
            "confidence_level must be a real number",
        ),
        (
            float("nan"),
            ValueError,
            "confidence_level must be finite",
        ),
        (
            float("inf"),
            ValueError,
            "confidence_level must be finite",
        ),
        (
            0.0,
            ValueError,
            "confidence_level must be between 0 and 1",
        ),
        (
            1.0,
            ValueError,
            "confidence_level must be between 0 and 1",
        ),
    ],
)
def test_rejects_invalid_confidence_level(
    value: object,
    error_type: type[Exception],
    message: str,
) -> None:
    with pytest.raises(
        error_type,
        match=message,
    ):
        build_plan(
            confidence_level=value,
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "resample_count",
        "block_length",
        "minimum_candidate_sample_size",
        "minimum_replication_count",
        "minimum_supporting_replication_count",
    ],
)
@pytest.mark.parametrize(
    (
        "value",
        "error_type",
        "message_suffix",
    ),
    [
        (
            True,
            TypeError,
            "must be an integer",
        ),
        (
            0,
            ValueError,
            "must be positive",
        ),
    ],
)
def test_rejects_invalid_positive_integer(
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


def test_rejects_single_resample() -> None:
    with pytest.raises(
        ValueError,
        match="resample_count must be at least 2",
    ):
        build_plan(
            resample_count=1,
        )


@pytest.mark.parametrize(
    (
        "value",
        "error_type",
        "message",
    ),
    [
        (
            True,
            TypeError,
            "random_seed must be an integer",
        ),
        (
            -1,
            ValueError,
            "random_seed must not be negative",
        ),
    ],
)
def test_rejects_invalid_random_seed(
    value: object,
    error_type: type[Exception],
    message: str,
) -> None:
    with pytest.raises(
        error_type,
        match=message,
    ):
        build_plan(
            random_seed=value,
        )


def test_rejects_support_requirement_above_total(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "minimum supporting replication count "
            "must not exceed minimum replication count"
        ),
    ):
        build_plan(
            minimum_replication_count=2,
            minimum_supporting_replication_count=3,
        )
