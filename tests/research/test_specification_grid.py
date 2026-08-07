import pytest

from src.indicators.descriptor import IndicatorDescriptor
from src.indicators.parameter_spaces import (
    ChoiceParameter,
    FloatParameter,
    IntegerParameter,
)
from src.indicators.research_space import (
    IndicatorOutput,
    IndicatorResearchSpace,
)
from src.research.specification_grid import (
    ResearchSpecificationGridError,
    ResearchSpecificationGridFactory,
)


def calculate(data: object, specification: object) -> object:
    return object()


def build_descriptor() -> IndicatorDescriptor:
    return IndicatorDescriptor(
        id="test_indicator",
        symbol="TEST",
        name="Test indicator",
        version=1,
        calculator=calculate,
        default_parameters={"period": 11},
        research_space=IndicatorResearchSpace(
            outputs=(IndicatorOutput(name="value"),),
            calculation_parameters={
                "period": IntegerParameter(
                    minimum=10,
                    maximum=12,
                    default=11,
                    step=1,
                ),
            },
            observation_parameters={
                "level": FloatParameter(
                    minimum=-80.0,
                    maximum=-78.0,
                    default=-79.0,
                    step=1.0,
                ),
                "direction": ChoiceParameter(
                    values=("cross_above", "cross_below"),
                    default="cross_above",
                ),
            },
            observation_types=("level_cross",),
            research_profiles=("overbought_oversold",),
            signal_rule_ids=("indicator_direction",),
        ),
    )


def test_expands_every_declared_parameter_combination() -> None:
    specifications = ResearchSpecificationGridFactory().create(
        build_descriptor()
    )

    assert len(specifications) == 18
    combinations = {
        (
            specification.calculation_parameter_values["period"],
            specification.observation_parameter_values["level"],
            specification.observation_parameter_values["direction"],
        )
        for specification in specifications
    }
    assert combinations == {
        (period, float(level), direction)
        for period in range(10, 13)
        for level in range(-80, -77)
        for direction in ("cross_above", "cross_below")
    }


def test_expansion_is_deterministic() -> None:
    factory = ResearchSpecificationGridFactory()

    first = factory.create(build_descriptor())
    second = factory.create(build_descriptor())

    assert tuple(item.fingerprint for item in first) == tuple(
        item.fingerprint for item in second
    )


def test_rejects_excessive_grid_before_materialization() -> None:
    factory = ResearchSpecificationGridFactory(
        maximum_specification_count=17,
    )

    with pytest.raises(
        ResearchSpecificationGridError,
        match="expands to 18 specifications",
    ):
        factory.create(build_descriptor())


def test_rejects_invalid_grid_limit() -> None:
    with pytest.raises(ValueError, match="must be positive"):
        ResearchSpecificationGridFactory(
            maximum_specification_count=0,
        )
