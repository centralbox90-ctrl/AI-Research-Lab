from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from numbers import Real


@dataclass(frozen=True, slots=True)
class HorizonStatistics:
    """
    Aggregate forward-return statistics for one horizon.
    """

    horizon: int
    sample_size: int
    mean_return: float
    median_return: float
    positive_rate: float
    minimum_return: float
    maximum_return: float

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

        if (
            not isinstance(self.sample_size, int)
            or isinstance(self.sample_size, bool)
        ):
            raise TypeError(
                "sample_size must be an integer"
            )

        if self.sample_size < 1:
            raise ValueError(
                "sample_size must be positive"
            )

        mean_return = self._validate_number(
            self.mean_return,
            field_name="mean_return",
        )
        median_return = self._validate_number(
            self.median_return,
            field_name="median_return",
        )
        positive_rate = self._validate_number(
            self.positive_rate,
            field_name="positive_rate",
        )
        minimum_return = self._validate_number(
            self.minimum_return,
            field_name="minimum_return",
        )
        maximum_return = self._validate_number(
            self.maximum_return,
            field_name="maximum_return",
        )

        if not 0.0 <= positive_rate <= 1.0:
            raise ValueError(
                "positive_rate must be between "
                "zero and one"
            )

        if minimum_return > maximum_return:
            raise ValueError(
                "minimum_return must not exceed "
                "maximum_return"
            )

        if not (
            minimum_return
            <= median_return
            <= maximum_return
        ):
            raise ValueError(
                "median_return must be within "
                "the return range"
            )

        if not (
            minimum_return
            <= mean_return
            <= maximum_return
        ):
            raise ValueError(
                "mean_return must be within "
                "the return range"
            )

        object.__setattr__(
            self,
            "mean_return",
            mean_return,
        )
        object.__setattr__(
            self,
            "median_return",
            median_return,
        )
        object.__setattr__(
            self,
            "positive_rate",
            positive_rate,
        )
        object.__setattr__(
            self,
            "minimum_return",
            minimum_return,
        )
        object.__setattr__(
            self,
            "maximum_return",
            maximum_return,
        )

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
