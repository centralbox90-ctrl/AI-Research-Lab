from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import TypeAlias

from src.indicators.series import IndicatorSeries


ObservationSignal: TypeAlias = int

ObservationCalculator: TypeAlias = Callable[
    [
        IndicatorSeries,
        Mapping[str, object],
    ],
    tuple[ObservationSignal, ...],
]


@dataclass(frozen=True, slots=True)
class ObservationDescriptor:
    """
    Description of one registered observation rule.
    """

    observation_type: str
    calculator: ObservationCalculator

    def __post_init__(self) -> None:
        if not isinstance(
            self.observation_type,
            str,
        ):
            raise TypeError(
                "observation_type must be a string"
            )

        observation_type = self.observation_type.strip()

        if not observation_type:
            raise ValueError(
                "observation_type must not be empty"
            )

        if not callable(self.calculator):
            raise TypeError(
                "calculator must be callable"
            )

        object.__setattr__(
            self,
            "observation_type",
            observation_type,
        )


class ObservationCalculationService:
    """
    Resolves and executes registered observation rules.

    The service does not contain indicator-specific or
    observation-specific calculation logic.
    """

    def __init__(
        self,
        descriptors: tuple[
            ObservationDescriptor,
            ...,
        ],
    ) -> None:
        registry: dict[
            str,
            ObservationDescriptor,
        ] = {}

        for descriptor in descriptors:
            observation_type = (
                descriptor.observation_type
            )

            if observation_type in registry:
                raise ValueError(
                    "Duplicate observation type: "
                    f"{observation_type}"
                )

            registry[observation_type] = descriptor

        self._registry = MappingProxyType(
            registry,
        )

    def calculate(
        self,
        *,
        series: IndicatorSeries,
        observation_type: str,
        parameters: Mapping[str, object],
    ) -> tuple[ObservationSignal, ...]:
        if not isinstance(
            series,
            IndicatorSeries,
        ):
            raise TypeError(
                "series must be an IndicatorSeries"
            )

        if not isinstance(
            observation_type,
            str,
        ):
            raise TypeError(
                "observation_type must be a string"
            )

        normalized_type = observation_type.strip()

        if not normalized_type:
            raise ValueError(
                "observation_type must not be empty"
            )

        descriptor = self._registry.get(
            normalized_type,
        )

        if descriptor is None:
            raise KeyError(
                "Unknown observation type: "
                f"{normalized_type}"
            )

        signals = tuple(
            descriptor.calculator(
                series,
                parameters,
            )
        )

        self._validate_signals(
            signals=signals,
            expected_length=len(series),
        )

        return signals

    @staticmethod
    def _validate_signals(
        *,
        signals: tuple[ObservationSignal, ...],
        expected_length: int,
    ) -> None:
        if len(signals) != expected_length:
            raise ValueError(
                "Observation result length must match "
                "indicator series length"
            )

        for signal in signals:
            if (
                not isinstance(signal, int)
                or isinstance(signal, bool)
                or signal not in (-1, 0, 1)
            ):
                raise ValueError(
                    "Observation signals must contain "
                    "only -1, 0, or 1"
                )
