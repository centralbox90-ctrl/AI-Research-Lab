from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from numbers import Real


@dataclass(frozen=True, slots=True)
class ForwardReturnOutcome:
    """
    Forward return measured after one observation.
    """

    observation_id: str
    horizon: int
    start_bar_index: int
    start_price: float
    end_price: float

    def __post_init__(self) -> None:
        if not isinstance(self.observation_id, str):
            raise TypeError(
                "observation_id must be a string"
            )

        normalized_observation_id = (
            self.observation_id.strip()
        )

        if not normalized_observation_id:
            raise ValueError(
                "observation_id must not be empty"
            )

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
            not isinstance(self.start_bar_index, int)
            or isinstance(self.start_bar_index, bool)
        ):
            raise TypeError(
                "start_bar_index must be an integer"
            )

        if self.start_bar_index < 0:
            raise ValueError(
                "start_bar_index must not be negative"
            )

        start_price = self._validate_price(
            self.start_price,
            field_name="start_price",
        )
        end_price = self._validate_price(
            self.end_price,
            field_name="end_price",
        )

        object.__setattr__(
            self,
            "observation_id",
            normalized_observation_id,
        )
        object.__setattr__(
            self,
            "start_price",
            start_price,
        )
        object.__setattr__(
            self,
            "end_price",
            end_price,
        )

    @property
    def end_bar_index(self) -> int:
        return self.start_bar_index + self.horizon

    @property
    def value(self) -> float:
        return (
            self.end_price / self.start_price
        ) - 1.0

    @staticmethod
    def _validate_price(
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

        if normalized_value <= 0.0:
            raise ValueError(
                f"{field_name} must be positive"
            )

        return normalized_value
