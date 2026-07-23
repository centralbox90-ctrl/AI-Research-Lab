from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from src.research.comparative_analysis import (
    ComparativeAnalysis,
)


@dataclass(frozen=True, slots=True)
class ExperimentResult:
    """
    Reproducible result of one completed research experiment.
    """

    id: str
    experiment_id: str
    analysis: ComparativeAnalysis
    created_at: datetime
    provenance: tuple[
        tuple[str, str],
        ...,
    ] = ()

    def __post_init__(self) -> None:
        result_id = self._validate_identifier(
            self.id,
            field_name="id",
        )
        experiment_id = self._validate_identifier(
            self.experiment_id,
            field_name="experiment_id",
        )

        if not isinstance(
            self.analysis,
            ComparativeAnalysis,
        ):
            raise TypeError(
                "analysis must be a "
                "ComparativeAnalysis"
            )

        if not isinstance(
            self.created_at,
            datetime,
        ):
            raise TypeError(
                "created_at must be a datetime"
            )

        if self.created_at.utcoffset() is None:
            raise ValueError(
                "created_at must be timezone-aware"
            )

        provenance = self._validate_provenance(
            self.provenance
        )

        object.__setattr__(
            self,
            "id",
            result_id,
        )
        object.__setattr__(
            self,
            "experiment_id",
            experiment_id,
        )
        object.__setattr__(
            self,
            "provenance",
            provenance,
        )

    @staticmethod
    def _validate_identifier(
        value: object,
        *,
        field_name: str,
    ) -> str:
        if not isinstance(value, str):
            raise TypeError(
                f"{field_name} must be a string"
            )

        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError(
                f"{field_name} must not be empty"
            )

        return normalized_value

    @classmethod
    def _validate_provenance(
        cls,
        values: object,
    ) -> tuple[tuple[str, str], ...]:
        if not isinstance(values, tuple):
            raise TypeError(
                "provenance must be a tuple"
            )

        normalized_values: list[
            tuple[str, str]
        ] = []
        keys: set[str] = set()

        for value in values:
            if (
                not isinstance(value, tuple)
                or len(value) != 2
            ):
                raise TypeError(
                    "each provenance value must be "
                    "a key-value tuple"
                )

            key = cls._validate_identifier(
                value[0],
                field_name="provenance key",
            )
            provenance_value = (
                cls._validate_identifier(
                    value[1],
                    field_name="provenance value",
                )
            )

            if key in keys:
                raise ValueError(
                    "provenance keys must be unique"
                )

            keys.add(key)
            normalized_values.append(
                (
                    key,
                    provenance_value,
                )
            )

        return tuple(normalized_values)
