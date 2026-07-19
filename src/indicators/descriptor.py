from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Literal, TypeAlias

import pandas as pd

from src.indicators.research_space import IndicatorResearchSpace
from src.indicators.series import IndicatorSeries
from src.indicators.specification import IndicatorSpecification


IndicatorCalculator: TypeAlias = Callable[
    [pd.DataFrame, IndicatorSpecification],
    IndicatorSeries,
]

CrossDirection: TypeAlias = Literal[
    "cross_above",
    "cross_below",
]


@dataclass(frozen=True, slots=True)
class NumericParameterSpace:
    minimum: float
    maximum: float
    step: float
    default: float | None = None
    coarse_values: tuple[float, ...] = ()

    def __post_init__(self) -> None:
        if self.minimum > self.maximum:
            raise ValueError(
                "minimum must be less than or equal to maximum."
            )

        if self.step <= 0:
            raise ValueError("step must be greater than zero.")

        if self.default is not None:
            self._validate_value(
                self.default,
                field_name="default",
            )

        coarse_values = tuple(self.coarse_values)

        for value in coarse_values:
            self._validate_value(
                value,
                field_name="coarse value",
            )

        if len(coarse_values) != len(set(coarse_values)):
            raise ValueError(
                "coarse values must not contain duplicates."
            )

        object.__setattr__(
            self,
            "coarse_values",
            coarse_values,
        )

    def _validate_value(
        self,
        value: float,
        *,
        field_name: str,
    ) -> None:
        if not self.minimum <= value <= self.maximum:
            raise ValueError(
                f"{field_name} must be within the parameter space."
            )


@dataclass(frozen=True, slots=True)
class IntegerParameterSpace:
    minimum: int
    maximum: int
    step: int
    default: int | None = None
    coarse_values: tuple[int, ...] = ()

    def __post_init__(self) -> None:
        if isinstance(self.minimum, bool) or not isinstance(
            self.minimum,
            int,
        ):
            raise TypeError("minimum must be an integer.")

        if isinstance(self.maximum, bool) or not isinstance(
            self.maximum,
            int,
        ):
            raise TypeError("maximum must be an integer.")

        if isinstance(self.step, bool) or not isinstance(
            self.step,
            int,
        ):
            raise TypeError("step must be an integer.")

        if self.minimum > self.maximum:
            raise ValueError(
                "minimum must be less than or equal to maximum."
            )

        if self.step <= 0:
            raise ValueError("step must be greater than zero.")

        if self.default is not None:
            self._validate_value(
                self.default,
                field_name="default",
            )

        coarse_values = tuple(self.coarse_values)

        for value in coarse_values:
            self._validate_value(
                value,
                field_name="coarse value",
            )

        if len(coarse_values) != len(set(coarse_values)):
            raise ValueError(
                "coarse values must not contain duplicates."
            )

        object.__setattr__(
            self,
            "coarse_values",
            coarse_values,
        )

    def _validate_value(
        self,
        value: int,
        *,
        field_name: str,
    ) -> None:
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"{field_name} must be an integer.")

        if not self.minimum <= value <= self.maximum:
            raise ValueError(
                f"{field_name} must be within the parameter space."
            )


@dataclass(frozen=True, slots=True)
class LevelCrossResearchProfile:
    level_space: NumericParameterSpace
    canonical_levels: tuple[float, ...]
    directions: tuple[CrossDirection, ...] = (
        "cross_above",
        "cross_below",
    )

    def __post_init__(self) -> None:
        canonical_levels = tuple(self.canonical_levels)
        directions = tuple(self.directions)

        invalid_levels = tuple(
            level
            for level in canonical_levels
            if not (
                self.level_space.minimum
                <= level
                <= self.level_space.maximum
            )
        )

        if invalid_levels:
            raise ValueError(
                "canonical levels must be within the level space."
            )

        supported_directions = {
            "cross_above",
            "cross_below",
        }
        unsupported_directions = set(directions) - supported_directions

        if unsupported_directions:
            unsupported = ", ".join(
                sorted(unsupported_directions)
            )
            raise ValueError(
                f"unsupported directions: {unsupported}."
            )

        if len(canonical_levels) != len(set(canonical_levels)):
            raise ValueError(
                "canonical levels must not contain duplicates."
            )

        if len(directions) != len(set(directions)):
            raise ValueError(
                "directions must not contain duplicates."
            )

        object.__setattr__(
            self,
            "canonical_levels",
            canonical_levels,
        )
        object.__setattr__(
            self,
            "directions",
            directions,
        )


ResearchProfile: TypeAlias = LevelCrossResearchProfile
ParameterSpace: TypeAlias = (
    IntegerParameterSpace | NumericParameterSpace
)


@dataclass(frozen=True, slots=True)
class IndicatorDescriptor:
    id: str
    symbol: str
    name: str
    version: int
    calculator: IndicatorCalculator
    default_parameters: Mapping[str, Any] = field(
        default_factory=dict
    )
    parameter_spaces: Mapping[str, ParameterSpace] = field(
        default_factory=dict
    )
    research_profiles: tuple[ResearchProfile, ...] = ()
    research_space: IndicatorResearchSpace | None = None
    def __post_init__(self) -> None:
        indicator_id = self.id.strip()
        symbol = self.symbol.strip()
        name = self.name.strip()

        if not indicator_id:
            raise ValueError("id must not be empty.")

        if not symbol:
            raise ValueError("symbol must not be empty.")

        if not name:
            raise ValueError("name must not be empty.")

        if isinstance(self.version, bool) or not isinstance(
            self.version,
            int,
        ):
            raise TypeError("version must be an integer.")

        if self.version < 1:
            raise ValueError(
                "version must be greater than zero."
            )

        if not callable(self.calculator):
            raise TypeError("calculator must be callable.")

        default_parameters = dict(self.default_parameters)
        parameter_spaces = dict(self.parameter_spaces)
        research_profiles = tuple(self.research_profiles)
        if (
           self.research_space is not None
           and not isinstance(
               self.research_space,
               IndicatorResearchSpace,
           )
        ):
           raise TypeError(
           "research_space must be an "
           "IndicatorResearchSpace or None."
           )

        unknown_defaults = (
            default_parameters.keys()
            - parameter_spaces.keys()
        )

        # parameter_spaces может быть пустым у старых дескрипторов.
        if parameter_spaces and unknown_defaults:
            unknown = ", ".join(sorted(unknown_defaults))
            raise ValueError(
                "default parameters do not have matching "
                f"parameter spaces: {unknown}."
            )

        for parameter_name, parameter_space in (
            parameter_spaces.items()
        ):
            if not parameter_name.strip():
                raise ValueError(
                    "parameter space name must not be empty."
                )

            if not isinstance(
                parameter_space,
                (
                    IntegerParameterSpace,
                    NumericParameterSpace,
                ),
            ):
                raise TypeError(
                    f"parameter space '{parameter_name}' has "
                    "an unsupported type."
                )

            if parameter_name in default_parameters:
                declared_default = parameter_space.default
                actual_default = default_parameters[
                    parameter_name
                ]

                if (
                    declared_default is not None
                    and actual_default != declared_default
                ):
                    raise ValueError(
                        f"default parameter '{parameter_name}' "
                        "does not match its parameter space default."
                    )

        object.__setattr__(self, "id", indicator_id)
        object.__setattr__(self, "symbol", symbol)
        object.__setattr__(self, "name", name)
        object.__setattr__(
            self,
            "default_parameters",
            MappingProxyType(default_parameters),
        )
        object.__setattr__(
            self,
            "parameter_spaces",
            MappingProxyType(parameter_spaces),
        )
        object.__setattr__(
            self,
            "research_profiles",
            research_profiles,
        )