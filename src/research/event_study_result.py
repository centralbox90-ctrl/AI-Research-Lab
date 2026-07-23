from __future__ import annotations

from dataclasses import dataclass

from src.research.outcome import (
    ForwardReturnOutcome,
)
from src.research.outcome_specification import (
    ForwardReturnSpecification,
)


@dataclass(frozen=True, slots=True)
class EventStudyResult:
    """
    Outcomes calculated for a collection of observations.
    """

    specification: ForwardReturnSpecification
    observation_ids: tuple[str, ...]
    outcomes: tuple[ForwardReturnOutcome, ...]
    incomplete_observation_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(
            self.specification,
            ForwardReturnSpecification,
        ):
            raise TypeError(
                "specification must be a "
                "ForwardReturnSpecification"
            )

        observation_ids = self._validate_ids(
            self.observation_ids,
            field_name="observation_ids",
        )
        incomplete_ids = self._validate_ids(
            self.incomplete_observation_ids,
            field_name=(
                "incomplete_observation_ids"
            ),
        )

        if set(observation_ids) & set(incomplete_ids):
            raise ValueError(
                "complete and incomplete observation "
                "ids must be disjoint"
            )

        if not isinstance(self.outcomes, tuple):
            raise TypeError(
                "outcomes must be a tuple"
            )

        for outcome in self.outcomes:
            if not isinstance(
                outcome,
                ForwardReturnOutcome,
            ):
                raise TypeError(
                    "each outcome must be a "
                    "ForwardReturnOutcome"
                )

        actual_pairs = tuple(
            (
                outcome.observation_id,
                outcome.horizon,
            )
            for outcome in self.outcomes
        )

        if len(actual_pairs) != len(
            set(actual_pairs)
        ):
            raise ValueError(
                "outcomes must not contain duplicate "
                "observation and horizon pairs"
            )

        expected_pairs = {
            (
                observation_id,
                horizon,
            )
            for observation_id in observation_ids
            for horizon in self.specification.horizons
        }

        if set(actual_pairs) != expected_pairs:
            raise ValueError(
                "outcomes must cover every complete "
                "observation and requested horizon"
            )

        object.__setattr__(
            self,
            "observation_ids",
            observation_ids,
        )
        object.__setattr__(
            self,
            "incomplete_observation_ids",
            incomplete_ids,
        )

    @property
    def observation_count(self) -> int:
        return len(self.observation_ids)

    @property
    def incomplete_observation_count(self) -> int:
        return len(
            self.incomplete_observation_ids
        )

    @property
    def outcome_count(self) -> int:
        return len(self.outcomes)

    @staticmethod
    def _validate_ids(
        values: object,
        *,
        field_name: str,
    ) -> tuple[str, ...]:
        if not isinstance(values, tuple):
            raise TypeError(
                f"{field_name} must be a tuple"
            )

        normalized_values: list[str] = []

        for value in values:
            if not isinstance(value, str):
                raise TypeError(
                    f"each {field_name} value must "
                    "be a string"
                )

            normalized_value = value.strip()

            if not normalized_value:
                raise ValueError(
                    f"each {field_name} value must "
                    "not be empty"
                )

            normalized_values.append(
                normalized_value
            )

        if len(normalized_values) != len(
            set(normalized_values)
        ):
            raise ValueError(
                f"{field_name} must not contain "
                "duplicates"
            )

        return tuple(normalized_values)
