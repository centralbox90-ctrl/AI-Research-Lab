from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ForwardReturnSpecification:
    """
    Defines forward returns measured after an observation.
    """

    horizons: tuple[int, ...]
    price_field: str = "close"

    def __post_init__(self) -> None:
        if not isinstance(self.horizons, tuple):
            raise TypeError(
                "horizons must be a tuple"
            )

        if not self.horizons:
            raise ValueError(
                "horizons must not be empty"
            )

        for horizon in self.horizons:
            if (
                not isinstance(horizon, int)
                or isinstance(horizon, bool)
            ):
                raise TypeError(
                    "each horizon must be an integer"
                )

            if horizon < 1:
                raise ValueError(
                    "each horizon must be positive"
                )

        if len(self.horizons) != len(
            set(self.horizons)
        ):
            raise ValueError(
                "horizons must not contain duplicates"
            )

        if not isinstance(self.price_field, str):
            raise TypeError(
                "price_field must be a string"
            )

        normalized_price_field = (
            self.price_field.strip()
        )

        if not normalized_price_field:
            raise ValueError(
                "price_field must not be empty"
            )

        object.__setattr__(
            self,
            "horizons",
            tuple(sorted(self.horizons)),
        )
        object.__setattr__(
            self,
            "price_field",
            normalized_price_field,
        )
