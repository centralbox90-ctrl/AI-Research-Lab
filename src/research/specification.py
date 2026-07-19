from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Mapping, TypeAlias


ParameterValue: TypeAlias = (
    None
    | bool
    | int
    | float
    | str
    | tuple["ParameterValue", ...]
    | tuple[tuple[str, "ParameterValue"], ...]
)

ParameterItems: TypeAlias = tuple[
    tuple[str, ParameterValue],
    ...,
]


def _freeze_value(value: object) -> ParameterValue:
    if value is None or isinstance(
        value,
        (bool, int, float, str),
    ):
        return value

    if isinstance(value, Mapping):
        return tuple(
            sorted(
                (
                    str(key),
                    _freeze_value(item),
                )
                for key, item in value.items()
            )
        )

    if isinstance(value, (list, tuple)):
        return tuple(
            _freeze_value(item)
            for item in value
        )

    raise TypeError(
        "Research specification parameter values must be "
        "JSON-compatible. "
        f"Received {type(value).__name__}."
    )


def _freeze_parameters(
    parameters: Mapping[str, object],
) -> ParameterItems:
    return tuple(
        sorted(
            (
                name,
                _freeze_value(value),
            )
            for name, value in parameters.items()
        )
    )


def _to_json_value(
    value: ParameterValue,
) -> object:
    if not isinstance(value, tuple):
        return value

    if all(
        isinstance(item, tuple)
        and len(item) == 2
        and isinstance(item[0], str)
        for item in value
    ):
        return {
            item[0]: _to_json_value(item[1])
            for item in value
        }

    return [
        _to_json_value(item)
        for item in value
    ]


def _parameters_to_dict(
    parameters: ParameterItems,
) -> dict[str, object]:
    return {
        name: _to_json_value(value)
        for name, value in parameters
    }


@dataclass(frozen=True, slots=True)
class IndicatorReference:
    indicator_id: str
    indicator_version: int

    def __post_init__(self) -> None:
        if not isinstance(self.indicator_id, str):
            raise TypeError(
                "indicator_id must be a string."
            )

        if not self.indicator_id.strip():
            raise ValueError(
                "indicator_id must not be empty."
            )

        if (
            not isinstance(self.indicator_version, int)
            or isinstance(self.indicator_version, bool)
        ):
            raise TypeError(
                "indicator_version must be an integer."
            )

        if self.indicator_version < 1:
            raise ValueError(
                "indicator_version must be at least 1."
            )


@dataclass(frozen=True, slots=True)
class ResearchSpecification:
    indicator: IndicatorReference
    output: str
    profile: str | None
    observation_type: str | None
    calculation_parameters: ParameterItems
    observation_parameters: ParameterItems

    def __post_init__(self) -> None:
        if not isinstance(
            self.indicator,
            IndicatorReference,
        ):
            raise TypeError(
                "indicator must be an IndicatorReference."
            )

        if not isinstance(self.output, str):
            raise TypeError(
                "output must be a string."
            )

        if not self.output.strip():
            raise ValueError(
                "output must not be empty."
            )

        if (
            self.profile is not None
            and not isinstance(self.profile, str)
        ):
            raise TypeError(
                "profile must be a string or None."
            )

        if (
            self.observation_type is not None
            and not isinstance(
                self.observation_type,
                str,
            )
        ):
            raise TypeError(
                "observation_type must be a string or None."
            )

    @classmethod
    def create(
        cls,
        *,
        indicator: IndicatorReference,
        output: str,
        profile: str | None,
        observation_type: str | None,
        calculation_parameters: Mapping[str, object],
        observation_parameters: Mapping[str, object],
    ) -> ResearchSpecification:
        return cls(
            indicator=indicator,
            output=output,
            profile=profile,
            observation_type=observation_type,
            calculation_parameters=_freeze_parameters(
                calculation_parameters
            ),
            observation_parameters=_freeze_parameters(
                observation_parameters
            ),
        )

    @property
    def calculation_parameter_values(
        self,
    ) -> dict[str, object]:
        return _parameters_to_dict(
            self.calculation_parameters
        )

    @property
    def observation_parameter_values(
        self,
    ) -> dict[str, object]:
        return _parameters_to_dict(
            self.observation_parameters
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "indicator": {
                "id": self.indicator.indicator_id,
                "version": (
                    self.indicator.indicator_version
                ),
            },
            "output": self.output,
            "profile": self.profile,
            "observation_type": (
                self.observation_type
            ),
            "calculation_parameters": (
                self.calculation_parameter_values
            ),
            "observation_parameters": (
                self.observation_parameter_values
            ),
        }

    @property
    def fingerprint(self) -> str:
        payload = json.dumps(
            self.to_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )

        return hashlib.sha256(
            payload.encode("utf-8")
        ).hexdigest()