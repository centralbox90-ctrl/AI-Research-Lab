from __future__ import annotations

import pandas as pd

from src.research.event_study_result import (
    EventStudyResult,
)
from src.research.outcome import (
    ForwardReturnOutcome,
)
from src.research.outcome_specification import (
    ForwardReturnSpecification,
)


class UnconditionalBaselineService:
    """
    Builds outcomes for every complete market-data point.
    """

    def build(
        self,
        *,
        data: pd.DataFrame,
        specification: ForwardReturnSpecification,
    ) -> EventStudyResult:
        if not isinstance(data, pd.DataFrame):
            raise TypeError(
                "data must be a pandas DataFrame"
            )

        if not isinstance(
            specification,
            ForwardReturnSpecification,
        ):
            raise TypeError(
                "specification must be a "
                "ForwardReturnSpecification"
            )

        if data.empty:
            raise ValueError(
                "data must not be empty"
            )

        price_field = specification.price_field

        if price_field not in data.columns:
            raise ValueError(
                f"data is missing price field "
                f"'{price_field}'"
            )

        complete_point_count = (
            len(data)
            - max(specification.horizons)
        )

        if complete_point_count < 1:
            raise ValueError(
                "data does not contain any complete "
                "baseline points"
            )

        observation_ids = tuple(
            self._build_observation_id(
                start_bar_index
            )
            for start_bar_index in range(
                complete_point_count
            )
        )

        outcomes = tuple(
            ForwardReturnOutcome(
                observation_id=(
                    self._build_observation_id(
                        start_bar_index
                    )
                ),
                horizon=horizon,
                start_bar_index=start_bar_index,
                start_price=data.iloc[
                    start_bar_index
                ][price_field],
                end_price=data.iloc[
                    start_bar_index + horizon
                ][price_field],
            )
            for start_bar_index in range(
                complete_point_count
            )
            for horizon in specification.horizons
        )

        return EventStudyResult(
            specification=specification,
            observation_ids=observation_ids,
            outcomes=outcomes,
        )

    @staticmethod
    def _build_observation_id(
        start_bar_index: int,
    ) -> str:
        return f"baseline:{start_bar_index}"
