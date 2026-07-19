from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from typing import Any

import pandas as pd

from src.indicators.series import IndicatorSeries
from src.indicators.specification import IndicatorSpecification
from src.indicators.technical import williams_r


class WilliamsRIndicator:
    """
    Adapter around the existing pandas Williams %R implementation.

    The class calculates a complete indicator series and does not
    interpret oversold, overbought, entry, exit, long, or short signals.
    """

    def __init__(
        self,
        specification: IndicatorSpecification,
    ) -> None:
        if specification.indicator_type != "williams_r":
            raise ValueError(
                "WilliamsRIndicator requires indicator_type='williams_r'"
            )

        period = specification.parameters.get(
            "period",
            14,
        )

        if isinstance(period, bool) or not isinstance(period, int):
            raise ValueError("period must be an integer")

        if period < 2:
            raise ValueError("period must be at least 2")

        self.specification = specification
        self.period = period

    def calculate(
        self,
        data: pd.DataFrame,
    ) -> IndicatorSeries:
        self._validate_data(data)

        calculated = williams_r(
            data,
            period=self.period,
        )

        timestamps = self._timestamps_from_index(
            calculated.index,
        )

        values = tuple(
            None if pd.isna(value) else float(value)
            for value in calculated
        )

        return IndicatorSeries.create(
            specification=self.specification,
            timestamps=timestamps,
            values=values,
            warmup_bars=self.period - 1,
            metadata={
                "implementation": (
                    "src.indicators.technical.williams_r"
                ),
            },
        )

    def _validate_data(
        self,
        data: pd.DataFrame,
    ) -> None:
        required_columns = {
            "High",
            "Low",
            "Close",
        }

        missing_columns = required_columns.difference(
            data.columns
        )

        if missing_columns:
            missing = ", ".join(
                sorted(missing_columns)
            )
            raise ValueError(
                f"missing required columns: {missing}"
            )

    def _timestamps_from_index(
        self,
        index: pd.Index,
    ) -> Sequence[datetime | Any]:
        return tuple(index.tolist())