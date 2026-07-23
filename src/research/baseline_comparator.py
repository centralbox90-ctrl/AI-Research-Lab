from __future__ import annotations

from src.research.horizon_comparison import (
    HorizonComparison,
)
from src.research.horizon_statistics import (
    HorizonStatistics,
)


class BaselineComparator:
    """
    Compares candidate statistics with a predefined baseline.
    """

    def compare(
        self,
        *,
        candidate: tuple[HorizonStatistics, ...],
        baseline: tuple[HorizonStatistics, ...],
    ) -> tuple[HorizonComparison, ...]:
        candidate_by_horizon = (
            self._index_statistics(
                candidate,
                field_name="candidate",
            )
        )
        baseline_by_horizon = (
            self._index_statistics(
                baseline,
                field_name="baseline",
            )
        )

        if (
            set(candidate_by_horizon)
            != set(baseline_by_horizon)
        ):
            raise ValueError(
                "candidate and baseline must contain "
                "the same horizons"
            )

        return tuple(
            self._compare_horizon(
                candidate=statistics,
                baseline=baseline_by_horizon[
                    statistics.horizon
                ],
            )
            for statistics in candidate
        )

    @staticmethod
    def _index_statistics(
        values: object,
        *,
        field_name: str,
    ) -> dict[int, HorizonStatistics]:
        if not isinstance(values, tuple):
            raise TypeError(
                f"{field_name} must be a tuple"
            )

        indexed: dict[int, HorizonStatistics] = {}

        for value in values:
            if not isinstance(
                value,
                HorizonStatistics,
            ):
                raise TypeError(
                    f"each {field_name} value must be "
                    "HorizonStatistics"
                )

            if value.horizon in indexed:
                raise ValueError(
                    f"{field_name} must not contain "
                    "duplicate horizons"
                )

            indexed[value.horizon] = value

        return indexed

    @staticmethod
    def _compare_horizon(
        *,
        candidate: HorizonStatistics,
        baseline: HorizonStatistics,
    ) -> HorizonComparison:
        return HorizonComparison(
            horizon=candidate.horizon,
            candidate_sample_size=(
                candidate.sample_size
            ),
            baseline_sample_size=(
                baseline.sample_size
            ),
            mean_return_difference=(
                candidate.mean_return
                - baseline.mean_return
            ),
            median_return_difference=(
                candidate.median_return
                - baseline.median_return
            ),
            positive_rate_difference=(
                candidate.positive_rate
                - baseline.positive_rate
            ),
        )
