from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from numbers import Real


@dataclass(frozen=True, slots=True)
class HorizonComparison:
    """
    Difference between candidate and baseline statistics.
    """

    horizon: int
    candidate_sample_size: int
    baseline_sample_size: int
    mean_return_difference: float
    median_return_difference: float
    positive_rate_difference: float

    def __post_init__(self) -> None:
        if (
            not isinstance(self.horizon, int)
            or isinstance(self.horizon, bool)
        ):
            raise TypeError(
                "horizon must be an integer"
            )

        if self.horizon < 1:
            raise ValueError(
                "horizon must be positive"
            )

        candidate_sample_size = (
            self._validate_sample_size(
                self.candidate_sample_size,
                field_name="candidate_sample_size",
            )
        )
        baseline_sample_size = (
            self._validate_sample_size(
                self.baseline_sample_size,
                field_name="baseline_sample_size",
            )
        )
        mean_return_difference = (
            self._validate_number(
                self.mean_return_difference,
                field_name=(
                    "mean_return_difference"
                ),
            )
        )
        median_return_difference = (
            self._validate_number(
                self.median_return_difference,
                field_name=(
                    "median_return_difference"
                ),
            )
        )
        positive_rate_difference = (
            self._validate_number(
                self.positive_rate_difference,
                field_name=(
                    "positive_rate_difference"
                ),
            )
        )

        if not (
            -1.0
            <= positive_rate_difference
            <= 1.0
        ):
            raise ValueError(
                "positive_rate_difference must be "
                "between minus one and one"
            )

        object.__setattr__(
            self,
            "candidate_sample_size",
            candidate_sample_size,
        )
        object.__setattr__(
            self,
            "baseline_sample_size",
            baseline_sample_size,
        )
        object.__setattr__(
            self,
            "mean_return_difference",
            mean_return_difference,
        )
        object.__setattr__(
            self,
            "median_return_difference",
            median_return_difference,
        )
        object.__setattr__(
            self,
            "positive_rate_difference",
            positive_rate_difference,
        )

    @staticmethod
    def _validate_sample_size(
        value: object,
        *,
        field_name: str,
    ) -> int:
        if (
            not isinstance(value, int)
            or isinstance(value, bool)
        ):
            raise TypeError(
                f"{field_name} must be an integer"
            )

        if value < 1:
            raise ValueError(
                f"{field_name} must be positive"
            )

        return value

    @staticmethod
    def _validate_number(
        value: object,
        *,
        field_name: str,
    ) -> float:
        if (
            not isinstance(value, Real)
            or isinstance(value, bool)
        ):
            raise TypeError(
                f"{field_name} must be a real number"
            )

        normalized_value = float(value)

        if not isfinite(normalized_value):
            raise ValueError(
                f"{field_name} must be finite"
            )

        return normalized_value
