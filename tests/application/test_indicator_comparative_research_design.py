from dataclasses import FrozenInstanceError

import pytest

from src.application.indicator_comparative_research_design import (
    IndicatorComparativeResearchDesign,
)
from src.research.outcome_specification import (
    ForwardReturnSpecification,
)
from src.research.specification import (
    IndicatorReference,
    ResearchSpecification,
)


def build_research_specification(
) -> ResearchSpecification:
    return ResearchSpecification.create(
        indicator=IndicatorReference(
            indicator_id="williams_r",
            indicator_version=1,
        ),
        output="williams_r",
        profile="overbought_oversold",
        observation_type="level_cross",
        calculation_parameters={
            "period": 14,
        },
        observation_parameters={
            "oversold_level": -80,
        },
    )


def build_design(
    **changes: object,
) -> IndicatorComparativeResearchDesign:
    values = {
        "research_specification": (
            build_research_specification()
        ),
        "outcome_specification": (
            ForwardReturnSpecification(
                horizons=(1, 5, 10),
            )
        ),
        "baseline": "unconditional",
    }
    values.update(changes)

    return IndicatorComparativeResearchDesign(
        **values
    )


def test_stores_predefined_research_design(
) -> None:
    design = build_design(
        baseline="  unconditional  "
    )

    assert (
        design.research_specification
        .indicator
        .indicator_id
        == "williams_r"
    )
    assert (
        design.outcome_specification.horizons
        == (1, 5, 10)
    )
    assert design.baseline == "unconditional"


def test_is_immutable() -> None:
    design = build_design()

    with pytest.raises(FrozenInstanceError):
        design.baseline = "other"


def test_rejects_invalid_research_specification(
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "research_specification must be a "
            "ResearchSpecification"
        ),
    ):
        build_design(
            research_specification=object()
        )


def test_rejects_invalid_outcome_specification(
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "outcome_specification must be a "
            "ForwardReturnSpecification"
        ),
    ):
        build_design(
            outcome_specification=object()
        )


def test_rejects_non_string_baseline() -> None:
    with pytest.raises(
        TypeError,
        match="baseline must be a string",
    ):
        build_design(
            baseline=object()
        )


@pytest.mark.parametrize(
    "invalid_baseline",
    (
        "",
        "random",
        "opposite_state",
    ),
)
def test_rejects_unsupported_baseline(
    invalid_baseline: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="baseline must be 'unconditional'",
    ):
        build_design(
            baseline=invalid_baseline
        )
