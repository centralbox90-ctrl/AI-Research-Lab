from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from src.indicators.parameter_spaces import (
    ParameterSpaceContract,
)


ParameterSpaces = Mapping[
    str,
    ParameterSpaceContract,
]


@dataclass(frozen=True, slots=True)
class IndicatorOutput:
    """Декларативное описание одного выхода индикатора."""

    name: str

    def __post_init__(self) -> None:
        normalized_name = self.name.strip()

        if not normalized_name:
            raise ValueError(
                "Indicator output name must not be empty."
            )

        object.__setattr__(
            self,
            "name",
            normalized_name,
        )


@dataclass(frozen=True, slots=True)
class IndicatorResearchSpace:
    """
    Декларативное описание допустимого исследовательского пространства.

    Модель ничего не вычисляет, не создаёт эксперименты и не выполняет
    наблюдения. Она только публикует возможности индикатора.
    """

    outputs: tuple[IndicatorOutput, ...]
    calculation_parameters: ParameterSpaces
    observation_parameters: ParameterSpaces
    observation_types: tuple[str, ...]
    research_profiles: tuple[str, ...]

    def __post_init__(self) -> None:
        outputs = tuple(self.outputs)
        calculation_parameters = dict(
            self.calculation_parameters
        )
        observation_parameters = dict(
            self.observation_parameters
        )
        observation_types = self._normalize_names(
            self.observation_types,
            field_name="observation type",
        )
        research_profiles = self._normalize_names(
            self.research_profiles,
            field_name="research profile",
        )

        if not outputs:
            raise ValueError(
                "Indicator research space must declare "
                "at least one output."
            )

        self._validate_unique_output_names(outputs)
        self._validate_parameter_names(
            calculation_parameters,
            field_name="calculation parameter",
        )
        self._validate_parameter_names(
            observation_parameters,
            field_name="observation parameter",
        )
        self._validate_disjoint_parameter_names(
            calculation_parameters,
            observation_parameters,
        )

        object.__setattr__(
            self,
            "outputs",
            outputs,
        )
        object.__setattr__(
            self,
            "calculation_parameters",
            MappingProxyType(
                calculation_parameters
            ),
        )
        object.__setattr__(
            self,
            "observation_parameters",
            MappingProxyType(
                observation_parameters
            ),
        )
        object.__setattr__(
            self,
            "observation_types",
            observation_types,
        )
        object.__setattr__(
            self,
            "research_profiles",
            research_profiles,
        )

    @staticmethod
    def _normalize_names(
        values: tuple[str, ...],
        *,
        field_name: str,
    ) -> tuple[str, ...]:
        normalized_values: list[str] = []

        for value in values:
            if not isinstance(value, str):
                raise TypeError(
                    f"Each {field_name} must be a string."
                )

            normalized_value = value.strip()

            if not normalized_value:
                raise ValueError(
                    f"{field_name.capitalize()} "
                    "must not be empty."
                )

            normalized_values.append(
                normalized_value
            )

        if len(normalized_values) != len(
            set(normalized_values)
        ):
            raise ValueError(
                f"Duplicate {field_name} declarations "
                "are not allowed."
            )

        return tuple(normalized_values)

    @staticmethod
    def _validate_unique_output_names(
        outputs: tuple[IndicatorOutput, ...],
    ) -> None:
        names = [
            output.name
            for output in outputs
        ]

        if len(names) != len(set(names)):
            raise ValueError(
                "Duplicate indicator output names "
                "are not allowed."
            )

    @staticmethod
    def _validate_parameter_names(
        parameters: dict[
            str,
            ParameterSpaceContract,
        ],
        *,
        field_name: str,
    ) -> None:
        for name, parameter_space in parameters.items():
            if not isinstance(name, str):
                raise TypeError(
                    f"{field_name.capitalize()} name "
                    "must be a string."
                )

            if not name.strip():
                raise ValueError(
                    f"{field_name.capitalize()} name "
                    "must not be empty."
                )

            if not isinstance(
                parameter_space,
                ParameterSpaceContract,
            ):
                raise TypeError(
                    f"{field_name.capitalize()} "
                    f"'{name}' must implement the "
                    "ParameterSpaceContract."
                )

    @staticmethod
    def _validate_disjoint_parameter_names(
        calculation_parameters: dict[
            str,
            ParameterSpaceContract,
        ],
        observation_parameters: dict[
            str,
            ParameterSpaceContract,
        ],
    ) -> None:
        duplicates = (
            calculation_parameters.keys()
            & observation_parameters.keys()
        )

        if duplicates:
            duplicate_names = ", ".join(
                sorted(duplicates)
            )
            raise ValueError(
                "Calculation and observation parameter "
                "names must be distinct. "
                f"Duplicates: {duplicate_names}."
            )