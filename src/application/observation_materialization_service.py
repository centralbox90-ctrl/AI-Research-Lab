from __future__ import annotations

from datetime import datetime

import pandas as pd

from src.application.indicator_research_result import (
    IndicatorResearchResult,
)
from src.research.observations.observation import (
    Observation,
)


class ObservationMaterializationService:
    """
    Converts indicator observation signals into domain observations.
    """

    def materialize(
        self,
        *,
        data: pd.DataFrame,
        result: IndicatorResearchResult,
        symbol: str,
        timeframe: str,
        price_field: str = "close",
    ) -> tuple[Observation, ...]:
        if not isinstance(data, pd.DataFrame):
            raise TypeError(
                "data must be a pandas DataFrame"
            )

        if not isinstance(
            result,
            IndicatorResearchResult,
        ):
            raise TypeError(
                "result must be an "
                "IndicatorResearchResult"
            )

        symbol = self._normalize_text(
            symbol,
            field_name="symbol",
        )
        timeframe = self._normalize_text(
            timeframe,
            field_name="timeframe",
        )
        price_field = self._normalize_text(
            price_field,
            field_name="price_field",
        )

        if len(data) != len(result.series):
            raise ValueError(
                "data and indicator series must have "
                "equal length"
            )

        if price_field not in data.columns:
            raise ValueError(
                f"data is missing price field "
                f"'{price_field}'"
            )

        specification = (
            result.research_specification
        )
        definition_id = specification.fingerprint

        return tuple(
            Observation(
                id=self._build_observation_id(
                    definition_id=definition_id,
                    symbol=symbol,
                    timeframe=timeframe,
                    bar_index=bar_index,
                    observation_signal=(
                        observation_signal
                    ),
                ),
                definition_id=definition_id,
                symbol=symbol,
                timeframe=timeframe,
                timestamp=self._resolve_timestamp(
                    data=data,
                    result=result,
                    bar_index=bar_index,
                ),
                bar_index=bar_index,
                price=data.iloc[
                    bar_index
                ][price_field],
                context={
                    "observation_signal": (
                        observation_signal
                    ),
                    "indicator_id": (
                        specification
                        .indicator
                        .indicator_id
                    ),
                    "indicator_output": (
                        specification.output
                    ),
                    "indicator_value": (
                        result.series.value_at(
                            bar_index
                        )
                    ),
                },
            )
            for (
                bar_index,
                observation_signal,
            ) in enumerate(result.observations)
            if observation_signal != 0
        )

    @staticmethod
    def _resolve_timestamp(
        *,
        data: pd.DataFrame,
        result: IndicatorResearchResult,
        bar_index: int,
    ) -> datetime:
        if "timestamp" not in data.columns:
            return result.series.timestamp_at(
                bar_index
            )

        timestamp = pd.to_datetime(
            data.iloc[bar_index]["timestamp"],
            utc=True,
        )

        return timestamp.to_pydatetime()

    @staticmethod
    def _normalize_text(
        value: object,
        *,
        field_name: str,
    ) -> str:
        if not isinstance(value, str):
            raise TypeError(
                f"{field_name} must be a string"
            )

        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError(
                f"{field_name} must not be empty"
            )

        return normalized_value

    @staticmethod
    def _build_observation_id(
        *,
        definition_id: str,
        symbol: str,
        timeframe: str,
        bar_index: int,
        observation_signal: int,
    ) -> str:
        return (
            f"{definition_id}:"
            f"{symbol}:"
            f"{timeframe}:"
            f"{bar_index}:"
            f"{observation_signal}"
        )
