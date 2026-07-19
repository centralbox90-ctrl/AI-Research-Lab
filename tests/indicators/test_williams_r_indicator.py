import pandas as pd
import pytest

from src.indicators.specification import IndicatorSpecification
from src.indicators.williams_r import WilliamsRIndicator


def make_specification(
    *,
    period: int = 3,
) -> IndicatorSpecification:
    return IndicatorSpecification(
        indicator_type="williams_r",
        version=1,
        parameters={
            "period": period,
        },
    )


def make_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "High": [
                10.0,
                12.0,
                14.0,
                16.0,
            ],
            "Low": [
                5.0,
                6.0,
                7.0,
                8.0,
            ],
            "Close": [
                8.0,
                9.0,
                10.0,
                12.0,
            ],
        },
        index=pd.date_range(
            start="2026-01-01",
            periods=4,
            freq="h",
            tz="UTC",
        ),
    )


def test_calculate_returns_indicator_series() -> None:
    indicator = WilliamsRIndicator(
        make_specification()
    )

    result = indicator.calculate(
        make_data()
    )

    assert result.specification == indicator.specification
    assert result.warmup_bars == 2
    assert len(result.timestamps) == 4
    assert len(result.values) == 4


def test_calculate_converts_warmup_nan_to_none() -> None:
    indicator = WilliamsRIndicator(
        make_specification()
    )

    result = indicator.calculate(
        make_data()
    )

    assert result.values[0] is None
    assert result.values[1] is None


def test_calculate_preserves_timestamps() -> None:
    data = make_data()

    indicator = WilliamsRIndicator(
        make_specification()
    )

    result = indicator.calculate(data)

    assert tuple(result.timestamps) == tuple(data.index)


def test_calculate_uses_existing_williams_formula() -> None:
    indicator = WilliamsRIndicator(
        make_specification()
    )

    result = indicator.calculate(
        make_data()
    )

    expected = -100.0 * (
        (14.0 - 10.0)
        / (14.0 - 5.0)
    )

    assert result.values[2] == pytest.approx(expected)


@pytest.mark.parametrize(
    "period",
    [
        0,
        1,
    ],
)
def test_rejects_period_below_two(
    period: int,
) -> None:
    with pytest.raises(
        ValueError,
        match="period must be at least 2",
    ):
        WilliamsRIndicator(
            make_specification(
                period=period,
            )
        )


def test_rejects_non_integer_period() -> None:
    specification = IndicatorSpecification(
        indicator_type="williams_r",
        version=1,
        parameters={
            "period": 3.5,
        },
    )

    with pytest.raises(
        ValueError,
        match="period must be an integer",
    ):
        WilliamsRIndicator(specification)


def test_rejects_incorrect_indicator_type() -> None:
    specification = IndicatorSpecification(
        indicator_type="rsi",
        version=1,
        parameters={
            "period": 14,
        },
    )

    with pytest.raises(
        ValueError,
        match="indicator_type='williams_r'",
    ):
        WilliamsRIndicator(specification)


def test_rejects_missing_market_columns() -> None:
    data = pd.DataFrame(
        {
            "Close": [
                1.0,
                2.0,
                3.0,
            ],
        }
    )

    indicator = WilliamsRIndicator(
        make_specification()
    )

    with pytest.raises(
        ValueError,
        match="missing required columns: High, Low",
    ):
        indicator.calculate(data)