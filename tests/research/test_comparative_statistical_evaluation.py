from dataclasses import FrozenInstanceError

import pytest

from src.research.comparative_statistical_evaluation import (
    ComparativeStatisticalEvaluation,
)


def build_evaluation(
    **overrides: object,
) -> ComparativeStatisticalEvaluation:
    arguments: dict[str, object] = {
        "research_fingerprint": "research-id",
        "dataset_id": "dataset-id",
        "horizon": 3,
        "candidate_sample_size": 100,
        "baseline_sample_size": 500,
        "effect_estimate": 0.001,
        "confidence_interval_lower": 0.0002,
        "confidence_interval_upper": 0.0018,
        "confidence_level": 0.95,
        "method": "moving_block_bootstrap",
        "resample_count": 2_000,
        "block_length": 5,
        "random_seed": 17,
        "warnings": (),
    }
    arguments.update(overrides)

    return ComparativeStatisticalEvaluation(
        **arguments,  # type: ignore[arg-type]
    )


def test_normalizes_and_freezes_evaluation(
) -> None:
    evaluation = build_evaluation(
        research_fingerprint="  research-id  ",
        dataset_id="  dataset-id  ",
        method="  moving_block_bootstrap  ",
        warnings=("  limited sample  ",),
    )

    assert evaluation.research_fingerprint == (
        "research-id"
    )
    assert evaluation.dataset_id == "dataset-id"
    assert evaluation.method == (
        "moving_block_bootstrap"
    )
    assert evaluation.warnings == (
        "limited sample",
    )
    assert isinstance(
        evaluation.effect_estimate,
        float,
    )

    with pytest.raises(FrozenInstanceError):
        setattr(evaluation, "horizon", 5)


@pytest.mark.parametrize(
    (
        "lower",
        "upper",
        "expected",
    ),
    [
        (0.1, 0.2, True),
        (-0.2, -0.1, True),
        (-0.1, 0.2, False),
        (0.0, 0.2, False),
        (-0.2, 0.0, False),
    ],
)
def test_reports_whether_interval_excludes_zero(
    lower: float,
    upper: float,
    expected: bool,
) -> None:
    evaluation = build_evaluation(
        confidence_interval_lower=lower,
        confidence_interval_upper=upper,
    )

    assert evaluation.excludes_zero is expected


@pytest.mark.parametrize(
    (
        "field_name",
        "value",
        "error_type",
        "message",
    ),
    [
        (
            "research_fingerprint",
            None,
            TypeError,
            "research_fingerprint must be a string",
        ),
        (
            "research_fingerprint",
            " ",
            ValueError,
            "research_fingerprint must not be empty",
        ),
        (
            "dataset_id",
            None,
            TypeError,
            "dataset_id must be a string",
        ),
        (
            "dataset_id",
            " ",
            ValueError,
            "dataset_id must not be empty",
        ),
        (
            "method",
            None,
            TypeError,
            "method must be a string",
        ),
        (
            "method",
            " ",
            ValueError,
            "method must not be empty",
        ),
    ],
)
def test_rejects_invalid_text_fields(
    field_name: str,
    value: object,
    error_type: type[Exception],
    message: str,
) -> None:
    with pytest.raises(
        error_type,
        match=message,
    ):
        build_evaluation(
            **{field_name: value},
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "horizon",
        "candidate_sample_size",
        "baseline_sample_size",
        "resample_count",
        "block_length",
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
def test_rejects_invalid_positive_integer_fields(
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
        build_evaluation(
            **{field_name: value},
        )


def test_rejects_candidate_larger_than_baseline(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "candidate_sample_size must not exceed "
            "baseline_sample_size"
        ),
    ):
        build_evaluation(
            candidate_sample_size=501,
        )


def test_rejects_block_larger_than_baseline(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "block_length must not exceed "
            "baseline_sample_size"
        ),
    ):
        build_evaluation(
            block_length=501,
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
        build_evaluation(
            random_seed=value,
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "effect_estimate",
        "confidence_interval_lower",
        "confidence_interval_upper",
        "confidence_level",
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
            None,
            TypeError,
            "must be a real number",
        ),
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
            float("inf"),
            ValueError,
            "must be finite",
        ),
        (
            float("-inf"),
            ValueError,
            "must be finite",
        ),
    ],
)
def test_rejects_invalid_real_fields(
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
        build_evaluation(
            **{field_name: value},
        )


@pytest.mark.parametrize(
    "confidence_level",
    [
        -0.1,
        0.0,
        1.0,
        1.1,
    ],
)
def test_rejects_invalid_confidence_level(
    confidence_level: float,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "confidence_level must be between "
            "0 and 1"
        ),
    ):
        build_evaluation(
            confidence_level=confidence_level,
        )


def test_rejects_inverted_confidence_interval(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "confidence interval lower bound must "
            "not exceed its upper bound"
        ),
    ):
        build_evaluation(
            confidence_interval_lower=0.2,
            confidence_interval_upper=0.1,
        )


@pytest.mark.parametrize(
    (
        "warnings",
        "error_type",
        "message",
    ),
    [
        (
            [],
            TypeError,
            "warnings must be a tuple",
        ),
        (
            (1,),
            TypeError,
            "each warning must be a string",
        ),
        (
            (" ",),
            ValueError,
            "each warning must not be empty",
        ),
    ],
)
def test_rejects_invalid_warnings(
    warnings: object,
    error_type: type[Exception],
    message: str,
) -> None:
    with pytest.raises(
        error_type,
        match=message,
    ):
        build_evaluation(
            warnings=warnings,
        )
