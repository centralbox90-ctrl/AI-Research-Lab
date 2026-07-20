from __future__ import annotations

from collections.abc import Hashable
from dataclasses import dataclass
from math import isfinite
from typing import (
    Generic,
    Protocol,
    TypeVar,
    runtime_checkable,
)


NumericParameterValue = TypeVar(
    "NumericParameterValue",
    int,
    float,
)
ChoiceValue = TypeVar(
    "ChoiceValue",
    bound=Hashable,
)


@runtime_checkable
class ParameterSpaceContract(Protocol):
    """
    Общий контракт декларативного пространства параметра.

    Research Engine зависит только от:
    - значения по умолчанию;
    - проверки принадлежности значения пространству.
    """

    @property
    def default(self) -> object:
        ...

    def contains(self, value: object) -> bool:
        ...


@dataclass(frozen=True, slots=True)
class ParameterSpace(
    Generic[NumericParameterValue],
):
    """Допустимый числовой диапазон одного параметра."""

    minimum: NumericParameterValue
    maximum: NumericParameterValue
    default: NumericParameterValue

    def __post_init__(self) -> None:
        if self.minimum > self.maximum:
            raise ValueError(
                "Parameter minimum must not be greater "
                "than maximum."
            )

        if not self.contains(self.default):
            raise ValueError(
                "Parameter default must be inside "
                "the allowed range."
            )

    def contains(self, value: object) -> bool:
        try:
            return self.minimum <= value <= self.maximum
        except TypeError:
            return False


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

    def contains(self, value: object) -> bool:
        if isinstance(value, bool) or not isinstance(value, int):
            return False

        return self.minimum <= value <= self.maximum


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

        object.__setattr__(
            self,
            "minimum",
            float(self.minimum),
        )
        object.__setattr__(
            self,
            "maximum",
            float(self.maximum),
        )
        object.__setattr__(
            self,
            "default",
            float(self.default),
        )

        super().__post_init__()

    def contains(self, value: object) -> bool:
        if isinstance(value, bool) or not isinstance(
            value,
            (int, float),
        ):
            return False

        numeric_value = float(value)

        if not isfinite(numeric_value):
            return False

        return self.minimum <= numeric_value <= self.maximum


@dataclass(frozen=True, slots=True)
class ChoiceParameter(Generic[ChoiceValue]):
    """
    Декларативное пространство дискретного параметра.

    Подходит для направлений, режимов, методов агрегации
    и других конечных наборов значений.
    """

    values: tuple[ChoiceValue, ...]
    default: ChoiceValue

    def __post_init__(self) -> None:
        values = tuple(self.values)

        if not values:
            raise ValueError(
                "Choice parameter must declare at least "
                "one value."
            )

        if len(values) != len(set(values)):
            raise ValueError(
                "Choice parameter values must be unique."
            )

        if self.default not in values:
            raise ValueError(
                "Choice parameter default must be one "
                "of its declared values."
            )

        object.__setattr__(
            self,
            "values",
            values,
        )

    def contains(self, value: object) -> bool:
        return value in self.values