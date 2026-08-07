import pytest

from src.application.research_specification_loader import (
    ResearchSpecificationLoader,
)


def build_payload() -> dict[str, object]:
    return {
        "indicator": {
            "id": "rsi",
            "version": 1,
        },
        "output": "rsi",
        "profile": None,
        "observation_type": "level_cross",
        "signal_rule_id": "long_on_observation",
        "calculation_parameters": {
            "period": 14,
        },
        "observation_parameters": {
            "level": 30.0,
            "direction": "cross_below",
        },
    }


def test_loads_rsi_specification() -> None:
    result = ResearchSpecificationLoader().from_dict(
        build_payload()
    )

    assert result.indicator.indicator_id == "rsi"
    assert result.indicator.indicator_version == 1

    assert (
        result.calculation_parameter_values
        == {"period": 14}
    )

    assert (
        result.observation_parameter_values
        == {
            "direction": "cross_below",
            "level": 30.0,
        }
    )


def test_rejects_non_object_payload() -> None:
    with pytest.raises(
        ValueError,
        match="must be an object",
    ):
        ResearchSpecificationLoader().from_dict([])


def test_rejects_missing_field() -> None:
    payload = build_payload()
    del payload["output"]

    with pytest.raises(
        ValueError,
        match="fields: output",
    ):
        ResearchSpecificationLoader().from_dict(
            payload
        )


def test_rejects_unknown_field() -> None:
    payload = build_payload()
    payload["python_callable"] = "unsafe"

    with pytest.raises(
        ValueError,
        match="fields: python_callable",
    ):
        ResearchSpecificationLoader().from_dict(
            payload
        )


def test_rejects_invalid_indicator_version() -> None:
    payload = build_payload()

    payload["indicator"] = {
        "id": "rsi",
        "version": 0,
    }

    with pytest.raises(
        ValueError,
        match="indicator_version must be at least 1",
    ):
        ResearchSpecificationLoader().from_dict(
            payload
        )
