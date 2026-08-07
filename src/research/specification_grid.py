from __future__ import annotations

from itertools import product
from math import prod

from src.indicators.descriptor import IndicatorDescriptor
from src.research.specification import ResearchSpecification
from src.research.specification_factory import (
    MissingResearchSpaceError,
    create_research_specification,
)


class ResearchSpecificationGridError(ValueError):
    """Base error for invalid or excessive specification grids."""


class ResearchSpecificationGridFactory:
    """Expand one indicator research space into concrete specifications."""

    DEFAULT_MAXIMUM_SPECIFICATION_COUNT = 100_000

    def __init__(
        self,
        *,
        maximum_specification_count: int = (
            DEFAULT_MAXIMUM_SPECIFICATION_COUNT
        ),
    ) -> None:
        if (
            isinstance(maximum_specification_count, bool)
            or not isinstance(maximum_specification_count, int)
        ):
            raise TypeError(
                "maximum_specification_count must be an integer"
            )
        if maximum_specification_count < 1:
            raise ValueError(
                "maximum_specification_count must be positive"
            )
        self._maximum_specification_count = (
            maximum_specification_count
        )

    def create(
        self,
        descriptor: IndicatorDescriptor,
    ) -> tuple[ResearchSpecification, ...]:
        if not isinstance(descriptor, IndicatorDescriptor):
            raise TypeError(
                "descriptor must be an IndicatorDescriptor"
            )

        space = descriptor.research_space
        if space is None:
            raise MissingResearchSpaceError(
                f"Indicator {descriptor.id!r} does not declare "
                "a research space."
            )

        calculation_names = tuple(
            space.calculation_parameters
        )
        observation_names = tuple(
            space.observation_parameters
        )
        calculation_grids = tuple(
            self._values(space.calculation_parameters[name])
            for name in calculation_names
        )
        observation_grids = tuple(
            self._values(space.observation_parameters[name])
            for name in observation_names
        )
        outputs = tuple(item.name for item in space.outputs)
        profiles: tuple[str | None, ...] = (
            tuple(space.research_profiles)
            if space.research_profiles
            else (None,)
        )
        observation_types: tuple[str | None, ...] = (
            tuple(space.observation_types)
            if space.observation_types
            else (None,)
        )
        signal_rules = tuple(space.signal_rule_ids)
        if not signal_rules:
            raise ResearchSpecificationGridError(
                "research space must declare at least one signal rule"
            )

        dimensions = (
            outputs,
            profiles,
            observation_types,
            signal_rules,
            *calculation_grids,
            *observation_grids,
        )
        count = prod(len(dimension) for dimension in dimensions)
        if count > self._maximum_specification_count:
            raise ResearchSpecificationGridError(
                f"research space expands to {count} specifications, "
                "exceeding maximum_specification_count "
                f"{self._maximum_specification_count}"
            )

        specifications: list[ResearchSpecification] = []
        fixed_dimension_count = 4
        for values in product(*dimensions):
            calculation_values = values[
                fixed_dimension_count:
                fixed_dimension_count + len(calculation_names)
            ]
            observation_values = values[
                fixed_dimension_count + len(calculation_names):
            ]
            specifications.append(
                create_research_specification(
                    descriptor,
                    output=values[0],
                    profile=values[1],
                    observation_type=values[2],
                    signal_rule_id=values[3],
                    calculation_parameters=dict(
                        zip(
                            calculation_names,
                            calculation_values,
                            strict=True,
                        )
                    ),
                    observation_parameters=dict(
                        zip(
                            observation_names,
                            observation_values,
                            strict=True,
                        )
                    ),
                )
            )

        fingerprints = tuple(
            specification.fingerprint
            for specification in specifications
        )
        if len(fingerprints) != len(set(fingerprints)):
            raise ResearchSpecificationGridError(
                "research space produced duplicate specifications"
            )
        return tuple(specifications)

    @staticmethod
    def _values(parameter_space: object) -> tuple[object, ...]:
        grid_values = getattr(parameter_space, "grid_values", None)
        if callable(grid_values):
            values = tuple(grid_values())
        else:
            try:
                values = (parameter_space.default,)
            except AttributeError as error:
                raise TypeError(
                    "parameter space must provide grid_values() "
                    "or default"
                ) from error
        if not values:
            raise ResearchSpecificationGridError(
                "parameter grid must not be empty"
            )
        return values
