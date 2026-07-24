import json
from dataclasses import FrozenInstanceError

import pytest

from src.research.campaign_design import (
    CampaignDesign,
)
from src.research.research_planner import (
    CampaignExperimentSpecification,
    ResearchCampaignPlan,
    ResearchPlanner,
)


def build_design(
    **overrides: object,
) -> CampaignDesign:
    values: dict[str, object] = {
        "question_id": "question-rsi",
        "hypothesis_ids": (
            "hypothesis-b",
            "hypothesis-a",
        ),
        "instruments": (
            "EURUSD",
            "BTCUSDT",
        ),
        "timeframes": (
            "H4",
            "H1",
        ),
        "data_periods": (
            "period-training",
        ),
        "indicator_configurations": (
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
            "walk-forward-v1"
        ),
        "evaluation_plan_ref": (
            "comparative-plan-v1"
        ),
        "provenance": (
            (
                "question_fingerprint",
                "question-fingerprint",
            ),
        ),
    }
    values.update(overrides)

    return CampaignDesign(**values)


def test_plans_complete_cartesian_experiment_space(
) -> None:
    design = build_design()
    plan = ResearchPlanner().plan(
        design
    )

    assert isinstance(
        plan,
        ResearchCampaignPlan,
    )
    assert plan.campaign_design_id == design.id
    assert plan.question_id == "question-rsi"
    assert plan.evaluation_plan_ref == (
        "comparative-plan-v1"
    )
    assert len(plan.experiment_specifications) == 8
    assert len(set(plan.experiment_ids)) == 8

    combinations = {
        (
            specification.hypothesis_id,
            specification.instrument,
            specification.timeframe,
        )
        for specification
        in plan.experiment_specifications
    }

    assert combinations == {
        (
            hypothesis_id,
            instrument,
            timeframe,
        )
        for hypothesis_id in (
            "hypothesis-a",
            "hypothesis-b",
        )
        for instrument in (
            "BTCUSDT",
            "EURUSD",
        )
        for timeframe in (
            "H1",
            "H4",
        )
    }


def test_planned_specifications_preserve_design_refs(
) -> None:
    design = build_design()
    plan = ResearchPlanner().plan(
        design
    )

    for specification in (
        plan.experiment_specifications
    ):
        assert isinstance(
            specification,
            CampaignExperimentSpecification,
        )
        assert specification.campaign_design_id == (
            design.id
        )
        assert specification.data_period == (
            "period-training"
        )
        assert (
            specification.indicator_configuration
            == "rsi:period:14"
        )
        assert specification.signal_rule == (
            "rsi-oversold-entry-v1"
        )
        assert specification.execution_policy == (
            "long-stop-take-v1"
        )
        assert specification.baseline == (
            "unconditional-return-v1"
        )
        assert specification.validation_strategy == (
            "walk-forward-v1"
        )


def test_plan_is_json_compatible() -> None:
    plan = ResearchPlanner().plan(
        build_design()
    )

    serialized = json.loads(
        json.dumps(
            plan.to_dict(),
            sort_keys=True,
        )
    )

    assert serialized["schema_version"] == 1
    assert serialized["id"] == plan.id
    assert serialized["campaign_design_id"] == (
        plan.campaign_design_id
    )
    assert len(
        serialized["experiment_specifications"]
    ) == 8
    assert serialized["provenance"] == {
        "campaign_design_fingerprint": (
            build_design().fingerprint
        ),
        "planner_version": (
            "research-planner-v1"
        ),
    }


def test_planning_is_deterministic() -> None:
    first = ResearchPlanner().plan(
        build_design()
    )
    second = ResearchPlanner().plan(
        build_design(
            hypothesis_ids=(
                "hypothesis-a",
                "hypothesis-b",
            ),
            instruments=(
                "BTCUSDT",
                "EURUSD",
            ),
            timeframes=(
                "H1",
                "H4",
            ),
        )
    )

    assert first.id == second.id
    assert first.fingerprint == second.fingerprint
    assert first.experiment_ids == (
        second.experiment_ids
    )


def test_changed_design_changes_plan_identity(
) -> None:
    first = ResearchPlanner().plan(
        build_design()
    )
    second = ResearchPlanner().plan(
        build_design(
            timeframes=(
                "D1",
                "H1",
            ),
        )
    )

    assert first.id != second.id
    assert first.fingerprint != second.fingerprint


def test_planner_version_changes_plan_identity(
) -> None:
    design = build_design()
    first = ResearchPlanner(
        version="research-planner-v1",
    ).plan(design)
    second = ResearchPlanner(
        version="research-planner-v2",
    ).plan(design)

    assert first.id != second.id
    assert first.provenance != second.provenance


def test_plan_is_immutable() -> None:
    plan = ResearchPlanner().plan(
        build_design()
    )

    with pytest.raises(FrozenInstanceError):
        plan.question_id = "other-question"


def test_planner_rejects_invalid_design() -> None:
    with pytest.raises(
        TypeError,
        match="design must be a CampaignDesign",
    ):
        ResearchPlanner().plan(
            object()
        )


def test_planner_limits_cartesian_expansion(
) -> None:
    design = build_design()

    with pytest.raises(
        ValueError,
        match=(
            "expands to 8 experiments, "
            "exceeding maximum_experiment_count 7"
        ),
    ):
        ResearchPlanner(
            maximum_experiment_count=7,
        ).plan(design)


@pytest.mark.parametrize(
    "value",
    (
        0,
        -1,
    ),
)
def test_maximum_experiment_count_must_be_positive(
    value: int,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "maximum_experiment_count "
            "must be positive"
        ),
    ):
        ResearchPlanner(
            maximum_experiment_count=value,
        )


@pytest.mark.parametrize(
    "value",
    (
        True,
        1.5,
        "10",
    ),
)
def test_maximum_experiment_count_must_be_integer(
    value: object,
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "maximum_experiment_count "
            "must be an integer"
        ),
    ):
        ResearchPlanner(
            maximum_experiment_count=value,
        )


def test_planner_version_must_not_be_empty(
) -> None:
    with pytest.raises(
        ValueError,
        match="version must not be empty",
    ):
        ResearchPlanner(
            version=" ",
        )