from __future__ import annotations

import pandas as pd

from src.research.observations.observation import (
    Observation,
)
from src.research.outcome import (
    ForwardReturnOutcome,
)
from src.research.outcome_specification import (
    ForwardReturnSpecification,
)


class ForwardOutcomeCalculator:
    """
    Calculates forward returns after one observation.
    """

    def calculate(
        self,
        *,
        data: pd.DataFrame,
        observation: Observation,
        specification: ForwardReturnSpecification,
    ) -> tuple[ForwardReturnOutcome, ...]:
        if not isinstance(data, pd.DataFrame):
            raise TypeError(
                "data must be a pandas DataFrame"
            )

        if not isinstance(observation, Observation):
            raise TypeError(
                "observation must be an Observation"
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

        start_bar_index = observation.bar_index

        if start_bar_index >= len(data):
            raise ValueError(
                "observation bar_index is outside data"
            )

        last_end_bar_index = (
            start_bar_index
            + max(specification.horizons)
        )

        if last_end_bar_index >= len(data):
            raise ValueError(
                "data does not contain all requested "
                "forward horizons"
            )

        start_price = data.iloc[
            start_bar_index
        ][price_field]

        return tuple(
            ForwardReturnOutcome(
                observation_id=observation.id,
                horizon=horizon,
                start_bar_index=start_bar_index,
                start_price=start_price,
                end_price=data.iloc[
                    start_bar_index + horizon
                ][price_field],
            )
            for horizon in specification.horizons
        )
