import math

import pandas as pd
import pytest

from src.indicators.technical import williams_r


def test_williams_r_returns_nan_during_warmup() -> None:
    data = pd.DataFrame(
        {
            "High": [
                10.0,
                12.0,
                14.0,
            ],
            "Low": [
                5.0,
                6.0,
                7.0,
            ],
            "Close": [
                8.0,
                9.0,
                10.0,
            ],
        }
    )

    result = williams_r(
        data,
        period=3,
    )

    assert math.isnan(result.iloc[0])
    assert math.isnan(result.iloc[1])


def test_williams_r_calculates_value_from_rolling_window() -> None:
    data = pd.DataFrame(
        {
            "High": [
                10.0,
                12.0,
                14.0,
            ],
            "Low": [
                5.0,
                6.0,
                7.0,
            ],
            "Close": [
                8.0,
                9.0,
                10.0,
            ],
        }
    )

    result = williams_r(
        data,
        period=3,
    )

    expected = -100.0 * (
        (14.0 - 10.0)
        / (14.0 - 5.0)
    )

    assert result.iloc[2] == pytest.approx(expected)


def test_williams_r_uses_only_current_rolling_window() -> None:
    data = pd.DataFrame(
        {
            "High": [
                100.0,
                10.0,
                12.0,
                14.0,
            ],
            "Low": [
                1.0,
                5.0,
                6.0,
                7.0,
            ],
            "Close": [
                50.0,
                8.0,
                9.0,
                10.0,
            ],
        }
    )

    result = williams_r(
        data,
        period=3,
    )

    expected = -100.0 * (
        (14.0 - 10.0)
        / (14.0 - 5.0)
    )

    assert result.iloc[3] == pytest.approx(expected)


def test_williams_r_returns_zero_at_highest_high() -> None:
    data = pd.DataFrame(
        {
            "High": [
                10.0,
                12.0,
                14.0,
            ],
            "Low": [
                5.0,
                6.0,
                7.0,
            ],
            "Close": [
                8.0,
                9.0,
                14.0,
            ],
        }
    )

    result = williams_r(
        data,
        period=3,
    )

    assert result.iloc[2] == pytest.approx(0.0)


def test_williams_r_returns_minus_one_hundred_at_lowest_low() -> None:
    data = pd.DataFrame(
        {
            "High": [
                10.0,
                12.0,
                14.0,
            ],
            "Low": [
                5.0,
                6.0,
                7.0,
            ],
            "Close": [
                8.0,
                9.0,
                5.0,
            ],
        }
    )

    result = williams_r(
        data,
        period=3,
    )

    assert result.iloc[2] == pytest.approx(-100.0)


def test_williams_r_returns_nan_for_flat_window() -> None:
    data = pd.DataFrame(
        {
            "High": [
                10.0,
                10.0,
                10.0,
            ],
            "Low": [
                10.0,
                10.0,
                10.0,
            ],
            "Close": [
                10.0,
                10.0,
                10.0,
            ],
        }
    )

    result = williams_r(
        data,
        period=3,
    )

    assert math.isnan(result.iloc[2])


def test_williams_r_preserves_dataframe_index() -> None:
    index = pd.date_range(
        start="2026-01-01",
        periods=3,
        freq="h",
        tz="UTC",
    )

    data = pd.DataFrame(
        {
            "High": [
                10.0,
                12.0,
                14.0,
            ],
            "Low": [
                5.0,
                6.0,
                7.0,
            ],
            "Close": [
                8.0,
                9.0,
                10.0,
            ],
        },
        index=index,
    )

    result = williams_r(
        data,
        period=3,
    )

    assert result.index.equals(index)