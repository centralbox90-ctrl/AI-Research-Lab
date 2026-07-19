import pytest

from src.indicators.specification import IndicatorSpecification


def test_indicator_specification_stores_configuration() -> None:
    specification = IndicatorSpecification(
        indicator_type="williams_r",
        version=1,
        parameters={
            "period": 14,
        },
    )

    assert specification.indicator_type == "williams_r"
    assert specification.version == 1
    assert specification.parameters == {
        "period": 14,
    }


def test_indicator_specification_normalizes_indicator_type() -> None:
    specification = IndicatorSpecification(
        indicator_type="  williams_r  ",
        version=1,
    )

    assert specification.indicator_type == "williams_r"


def test_indicator_specification_rejects_empty_indicator_type() -> None:
    with pytest.raises(
        ValueError,
        match="indicator_type must not be empty",
    ):
        IndicatorSpecification(
            indicator_type=" ",
            version=1,
        )


def test_indicator_specification_rejects_invalid_version() -> None:
    with pytest.raises(
        ValueError,
        match="version must be greater than or equal to one",
    ):
        IndicatorSpecification(
            indicator_type="williams_r",
            version=0,
        )


def test_indicator_specification_copies_parameters() -> None:
    parameters = {
        "period": 14,
    }

    specification = IndicatorSpecification(
        indicator_type="williams_r",
        version=1,
        parameters=parameters,
    )

    parameters["period"] = 20

    assert specification.parameters["period"] == 14


def test_indicator_specification_parameters_are_read_only() -> None:
    specification = IndicatorSpecification(
        indicator_type="williams_r",
        version=1,
        parameters={
            "period": 14,
        },
    )

    with pytest.raises(TypeError):
        specification.parameters["period"] = 20