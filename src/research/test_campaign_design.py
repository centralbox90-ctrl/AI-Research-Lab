from dataclasses import FrozenInstanceError

import pytest

from src.research.campaign_design import (
    CampaignDesign,
)


def build_design(
    **overrides: object,
) -> CampaignDesign:
    values: dict[str, object] = {
        "question_id": " question-rsi ",
        "hypothesis_ids": (
            "hypothesis-b",
            "hypothesis-a",
        ),
        "instruments": (
            "BTCUSDT",
            "EURUSD",
        ),
        "timeframes": (
            "H4",
            "H1",
        ),
        "data_periods": (
            "period-out-of-sample",
            "period-training",
        ),
        "indicator_configurations": (
            "rsi:period:21",
            "rsi:period:14",
        ),
        "signal_rules": (
            "rsi-oversold-entry-v1",
        ),
        "execution_policies": (
            "long-stop-take-v1",
        ),
        "baselines": (
            "unconditional-return-v1",
        ),
        "validation_strategy": (
            " walk-forward-v1 "
        ),
        "evaluation_plan_ref": (
            " comparative-plan-v1 "
        ),
        "provenance": (
            (
                "planner_version",
                "campaign-planner-v1",
            ),
            (
                "question_fingerprint",
                "question-fingerprint",
            ),
        ),
    }
    values.update(overrides)

    return CampaignDesign(**values)


def test_creates_normalized_campaign_design(
) -> None:
    design = build_design()

    assert design.question_id == "question-rsi"
    assert design.hypothesis_ids == (
        "hypothesis-a",
        "hypothesis-b",
    )
    assert design.instruments == (
        "BTCUSDT",
        "EURUSD",
    )
    assert design.timeframes == (
        "H1",
        "H4",
    )
    assert design.indicator_configurations == (
        "rsi:period:14",
        "rsi:period:21",
    )
    assert design.validation_strategy == (
        "walk-forward-v1"
    )
    assert design.evaluation_plan_ref == (
        "comparative-plan-v1"
    )
    assert design.id.startswith(
        "campaign-design:sha256:"
    )
    assert len(design.fingerprint) == 64


def test_serializes_campaign_design(
) -> None:
    design = build_design()
    serialized = design.to_dict()

    assert serialized["schema_version"] == 1
    assert serialized["id"] == design.id
    assert serialized["hypothesis_ids"] == [
        "hypothesis-a",
        "hypothesis-b",
    ]
    assert serialized["timeframes"] == [
        "H1",
        "H4",
    ]
    assert serialized["validation_strategy"] == (
        "walk-forward-v1"
    )
    assert serialized["provenance"] == {
        "planner_version": "campaign-planner-v1",
        "question_fingerprint": (
            "question-fingerprint"
        ),
    }


def test_design_is_immutable() -> None:
    design = build_design()

    with pytest.raises(FrozenInstanceError):
        design.question_id = "other-question"


def test_identity_is_independent_of_input_order(
) -> None:
    first = build_design()
    second = build_design(
        hypothesis_ids=(
            "hypothesis-a",
            "hypothesis-b",
        ),
        instruments=(
            "EURUSD",
            "BTCUSDT",
        ),
        timeframes=(
            "H1",
            "H4",
        ),
        indicator_configurations=(
            "rsi:period:14",
            "rsi:period:21",
        ),
        provenance=(
            (
                "question_fingerprint",
                "question-fingerprint",
            ),
            (
                "planner_version",
                "campaign-planner-v1",
            ),
        ),
    )

    assert first.id == second.id
    assert first.fingerprint == second.fingerprint


def test_changed_dimension_changes_identity(
) -> None:
    first = build_design()
    second = build_design(
        timeframes=(
            "D1",
            "H1",
        ),
    )

    assert first.id != second.id
    assert first.fingerprint != second.fingerprint


@pytest.mark.parametrize(
    "field_name",
    (
        "hypothesis_ids",
        "instruments",
        "timeframes",
        "data_periods",
        "indicator_configurations",
        "signal_rules",
        "execution_policies",
        "baselines",
    ),
)
def test_dimension_must_be_tuple(
    field_name: str,
) -> None:
    with pytest.raises(
        TypeError,
        match=f"{field_name} must be a tuple",
    ):
        build_design(
            **{
                field_name: [
                    "invalid",
                ],
            }
        )


@pytest.mark.parametrize(
    "field_name",
    (
        "hypothesis_ids",
        "instruments",
        "timeframes",
        "data_periods",
        "indicator_configurations",
        "signal_rules",
        "execution_policies",
        "baselines",
    ),
)
def test_dimension_must_not_be_empty(
    field_name: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=f"{field_name} must not be empty",
    ):
        build_design(
            **{
                field_name: (),
            }
        )


def test_dimension_rejects_duplicates() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "timeframes must not contain duplicates"
        ),
    ):
        build_design(
            timeframes=(
                "H1",
                "H1",
            ),
        )


@pytest.mark.parametrize(
    "field_name",
    (
        "question_id",
        "validation_strategy",
        "evaluation_plan_ref",
    ),
)
def test_required_text_must_not_be_empty(
    field_name: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=f"{field_name} must not be empty",
    ):
        build_design(
            **{
                field_name: " ",
            }
        )


def test_provenance_requires_unique_keys(
) -> None:
    with pytest.raises(
        ValueError,
        match="provenance keys must be unique",
    ):
        build_design(
            provenance=(
                (
                    "planner_version",
                    "v1",
                ),
                (
                    "planner_version",
                    "v2",
                ),
            ),
        )


def test_provenance_must_not_be_empty(
) -> None:
    with pytest.raises(
        ValueError,
        match="provenance must not be empty",
    ):
        build_design(
            provenance=(),
        )