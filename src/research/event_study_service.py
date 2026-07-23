from __future__ import annotations

import pandas as pd

from src.research.event_study_result import (
    EventStudyResult,
)
from src.research.forward_outcome_calculator import (
    ForwardOutcomeCalculator,
)
from src.research.observations.observation import (
    Observation,
)
from src.research.outcome import (
    ForwardReturnOutcome,
)
from src.research.outcome_specification import (
    ForwardReturnSpecification,
)


class EventStudyService:
    """
    Calculates forward outcomes for a collection of observations.
    """

    def run(
        self,
        *,
        data: pd.DataFrame,
        observations: tuple[Observation, ...],
        specification: ForwardReturnSpecification,
    ) -> EventStudyResult:
        if not isinstance(data, pd.DataFrame):
            raise TypeError(
                "data must be a pandas DataFrame"
            )

        if not isinstance(observations, tuple):
            raise TypeError(
                "observations must be a tuple"
            )

        if not isinstance(
            specification,
            ForwardReturnSpecification,
        ):
            raise TypeError(
                "specification must be a "
                "ForwardReturnSpecification"
            )

        for observation in observations:
            if not isinstance(observation, Observation):
                raise TypeError(
                    "each observation must be an "
                    "Observation"
                )

        observation_ids = tuple(
            observation.id
            for observation in observations
        )

        if len(observation_ids) != len(
            set(observation_ids)
        ):
            raise ValueError(
                "observations must have unique ids"
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

        calculator = ForwardOutcomeCalculator()
        complete_ids: list[str] = []
        incomplete_ids: list[str] = []
        outcomes: list[ForwardReturnOutcome] = []
        maximum_horizon = max(
            specification.horizons
        )

        for observation in observations:
            if observation.bar_index >= len(data):
                raise ValueError(
                    "observation bar_index is outside data"
                )

            if (
                observation.bar_index
                + maximum_horizon
                >= len(data)
            ):
                incomplete_ids.append(
                    observation.id
                )
                continue

            complete_ids.append(
                observation.id
            )
            outcomes.extend(
                calculator.calculate(
                    data=data,
                    observation=observation,
                    specification=specification,
                )
            )

        return EventStudyResult(
            specification=specification,
            observation_ids=tuple(complete_ids),
            outcomes=tuple(outcomes),
            incomplete_observation_ids=tuple(
                incomplete_ids
            ),
        )
