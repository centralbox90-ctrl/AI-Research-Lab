from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Generic, TypeVar


ParameterValue = TypeVar("ParameterValue", int, float)


@dataclass(frozen=True, slots=True)
class ParameterSpace(Generic[ParameterValue]):
    """Допустимое пространство значений одного параметра."""

    minimum: ParameterValue
    maximum: ParameterValue
    default: ParameterValue

    def __post_init__(self) -> None:
        if self.minimum > self.maximum:
            raise ValueError(
                "Parameter minimum must not be greater than maximum."
            )

        if not self.contains(self.default):
            raise ValueError(
                "Parameter default must be inside the allowed range."
            )

    def contains(self, value: ParameterValue) -> bool:
        return self.minimum <= value <= self.maximum


@dataclass(frozen=True, slots=True)
class IntegerParameter(ParameterSpace[int]):
    """Декларативное пространство целочисленного параметра."""

    minimum: int
    maximum: int
    default: int

    def __post_init__(self) -> None:
        for field_name, value in (
            ("minimum", self.minimum),
            ("maximum", self.maximum),
            ("default", self.default),
        ):
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(
                    f"{field_name} must be an integer."
                )

        super().__post_init__()


@dataclass(frozen=True, slots=True)
class FloatParameter(ParameterSpace[float]):
    """Декларативное пространство числового параметра."""

    minimum: float
    maximum: float
    default: float

    def __post_init__(self) -> None:
        values = (
            ("minimum", self.minimum),
            ("maximum", self.maximum),
            ("default", self.default),
        )

        for field_name, value in values:
            if isinstance(value, bool) or not isinstance(
                value,
                (int, float),
            ):
                raise TypeError(
                    f"{field_name} must be a finite number."
                )

            if not isfinite(float(value)):
                raise ValueError(
                    f"{field_name} must be finite."
                )

        object.__setattr__(self, "minimum", float(self.minimum))
        object.__setattr__(self, "maximum", float(self.maximum))
        object.__setattr__(self, "default", float(self.default))

        super().__post_init__()