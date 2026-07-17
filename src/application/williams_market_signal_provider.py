from __future__ import annotations

import pandas as pd

from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
)
from src.application.market_signal_provider import (
    MarketSignalProvider,
)
from src.indicators.technical import williams_r


class WilliamsMarketSignalProvider(
    MarketSignalProvider,
):
    """
    Generates Williams %R reversal signals.

    LONG:
        Williams %R crosses upward through the oversold level.

    SHORT:
        Williams %R crosses downward through the overbought level.

    The provider only prepares signals. It does not execute trades.
    """

    def generate(
        self,
        data: pd.DataFrame,
        specification: MarketExperimentSpecification,
    ) -> pd.DataFrame:
        prepared = data.copy()

        period = self._get_integer_parameter(
            specification,
            name="williams_period",
            default=14,
            minimum=2,
        )

        oversold_level = self._get_float_parameter(
            specification,
            name="williams_oversold",
            default=-80.0,
        )

        overbought_level = self._get_float_parameter(
            specification,
            name="williams_overbought",
            default=-20.0,
        )

        if oversold_level >= overbought_level:
            raise ValueError(
                "williams_oversold must be lower than "
                "williams_overbought"
            )

        prepared["Williams_R"] = williams_r(
            prepared,
            period=period,
        )

        previous_williams = prepared["Williams_R"].shift(1)

        long_signal = (
            (previous_williams <= oversold_level)
            & (prepared["Williams_R"] > oversold_level)
        )

        short_signal = (
            (previous_williams >= overbought_level)
            & (prepared["Williams_R"] < overbought_level)
        )

        prepared["AI_prediction"] = 0

        prepared.loc[
            long_signal,
            "AI_prediction",
        ] = 1

        prepared.loc[
            short_signal,
            "AI_prediction",
        ] = -1

        prepared["AI_prediction"] = (
            prepared["AI_prediction"]
            .fillna(0)
            .astype(int)
        )

        return prepared

    def _get_integer_parameter(
        self,
        specification: MarketExperimentSpecification,
        *,
        name: str,
        default: int,
        minimum: int,
    ) -> int:
        value = specification.strategy_parameters.get(
            name,
            default,
        )

        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(
                f"{name} must be an integer"
            )

        if value < minimum:
            raise ValueError(
                f"{name} must be at least {minimum}"
            )

        return value

    def _get_float_parameter(
        self,
        specification: MarketExperimentSpecification,
        *,
        name: str,
        default: float,
    ) -> float:
        value = specification.strategy_parameters.get(
            name,
            default,
        )

        if isinstance(value, bool) or not isinstance(
            value,
            (int, float),
        ):
            raise ValueError(
                f"{name} must be numeric"
            )

        return float(value)