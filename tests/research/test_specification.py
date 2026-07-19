from __future__ import annotations

from src.research.specification import (
    IndicatorReference,
    ResearchSpecification,
)


def test_equivalent_specifications_have_same_fingerprint():
    first = ResearchSpecification.create(
        indicator=IndicatorReference(
            indicator_id="example",
            indicator_version=1,
        ),
        output="value",
        profile="level_cross",
        observation_type="cross_above",
        calculation_parameters={
            "slow": 20,
            "fast": 5,
        },
        observation_parameters={
            "level": 10.0,
        },
    )

    second = ResearchSpecification.create(
        indicator=IndicatorReference(
            indicator_id="example",
            indicator_version=1,
        ),
        output="value",
        profile="level_cross",
        observation_type="cross_above",
        calculation_parameters={
            "fast": 5,
            "slow": 20,
        },
        observation_parameters={
            "level": 10.0,
        },
    )

    assert first == second
    assert first.fingerprint == second.fingerprint


def test_parameter_order_does_not_change_serialization():
    specification = ResearchSpecification.create(
        indicator=IndicatorReference(
            indicator_id="example",
            indicator_version=1,
        ),
        output="value",
        profile=None,
        observation_type=None,
        calculation_parameters={
            "second": 2,
            "first": 1,
        },
        observation_parameters={},
    )

    assert (
        specification.calculation_parameter_values
        == {
            "first": 1,
            "second": 2,
        }
    )