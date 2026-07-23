from __future__ import annotations

from statistics import fmean, median

from src.research.event_study_result import (
    EventStudyResult,
)
from src.research.horizon_statistics import (
    HorizonStatistics,
)


class EventStudyAnalyzer:
    """
    Aggregates event-study outcomes by forward horizon.
    """

    def analyze(
        self,
        result: EventStudyResult,
    ) -> tuple[HorizonStatistics, ...]:
        if not isinstance(result, EventStudyResult):
            raise TypeError(
                "result must be an EventStudyResult"
            )

        if not result.observation_ids:
            return ()

        return tuple(
            self._analyze_horizon(
                result=result,
                horizon=horizon,
            )
            for horizon in (
                result.specification.horizons
            )
        )

    @staticmethod
    def _analyze_horizon(
        *,
        result: EventStudyResult,
        horizon: int,
    ) -> HorizonStatistics:
        values = tuple(
            outcome.value
            for outcome in result.outcomes
            if outcome.horizon == horizon
        )

        positive_count = sum(
            value > 0.0
            for value in values
        )

        return HorizonStatistics(
            horizon=horizon,
            sample_size=len(values),
            mean_return=fmean(values),
            median_return=median(values),
            positive_rate=(
                positive_count / len(values)
            ),
            minimum_return=min(values),
            maximum_return=max(values),
        )
