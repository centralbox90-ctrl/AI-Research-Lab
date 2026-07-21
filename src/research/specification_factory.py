from __future__ import annotations

from collections.abc import Mapping, Sequence

from src.indicators.descriptor import IndicatorDescriptor
from src.research.specification import (
    IndicatorReference,
    ResearchSpecification,
)


class ResearchSpecificationError(ValueError):
    """Base research specification error."""


class MissingResearchSpaceError(
    ResearchSpecificationError
):
    """Indicator has no declared research space."""


class UnsupportedOutputError(
    ResearchSpecificationError
):
    """Requested output is not supported."""


class UnsupportedProfileError(
    ResearchSpecificationError
):
    """Requested research profile is not supported."""


class UnsupportedObservationTypeError(
    ResearchSpecificationError
):
    """Requested observation type is not supported."""


class UnknownParameterError(
    ResearchSpecificationError
):
    """A parameter is not declared by the indicator."""


class MissingParameterError(
    ResearchSpecificationError
):
    """A required parameter has no supplied or default value."""


class InvalidParameterValueError(
    ResearchSpecificationError
):
    """A parameter value is outside its declared space."""


_UNSET = object()


def _select_option(
    *,
    requested: object,
    available: Sequence[str],
    option_name: str,
    error_type: type[ResearchSpecificationError],
) -> str | None:
    if requested is _UNSET:
        if not available:
            return None

        return available[0]

    if requested is None:
        if available:
            raise error_type(
                f"{option_name} is required. "
                f"Available values: {tuple(available)!r}."
            )

        return None

    if not isinstance(requested, str):
        raise TypeError(
            f"{option_name} must be a string or None."
        )

    if requested not in available:
        raise error_type(
            f"Unsupported {option_name} "
            f"{requested!r}. "
            f"Available values: {tuple(available)!r}."
        )

    return requested


def _resolve_parameters(
    *,
    supplied: Mapping[str, object] | None,
    spaces: Mapping[str, object],
    parameter_group: str,
) -> dict[str, object]:
    supplied_values = dict(supplied or {})

    unknown_names = (
        supplied_values.keys()
        - spaces.keys()
    )

    if unknown_names:
        formatted = ", ".join(
            sorted(unknown_names)
        )
        raise UnknownParameterError(
            f"Unknown {parameter_group} "
            f"parameter(s): {formatted}."
        )

    resolved: dict[str, object] = {}

    for name, space in spaces.items():
        if name in supplied_values:
            value = supplied_values[name]
        else:
            try:
                value = space.default
            except AttributeError as error:
                raise MissingParameterError(
                    f"{parameter_group} parameter "
                    f"{name!r} has no supplied value "
                    "and no declared default."
                ) from error

        try:
            is_valid = space.contains(value)
        except AttributeError as error:
            raise TypeError(
                f"Parameter space for {name!r} "
                "must provide default and contains()."
            ) from error

        if not is_valid:
            raise InvalidParameterValueError(
                f"Invalid value {value!r} for "
                f"{parameter_group} parameter "
                f"{name!r}."
            )

        resolved[name] = value

    return resolved


def create_research_specification(
    descriptor: IndicatorDescriptor,
    *,
    output: str | object = _UNSET,
    profile: str | None | object = _UNSET,
    observation_type: str | None | object = _UNSET,
    signal_rule_id: str | object = _UNSET,

    calculation_parameters: (
        Mapping[str, object] | None
    ) = None,
    observation_parameters: (
        Mapping[str, object] | None
    ) = None,
) -> ResearchSpecification:
    if not isinstance(
        descriptor,
        IndicatorDescriptor,
    ):
        raise TypeError(
            "descriptor must be an "
            "IndicatorDescriptor."
        )

    research_space = descriptor.research_space

    if research_space is None:
        raise MissingResearchSpaceError(
            f"Indicator {descriptor.id!r} "
            "does not declare a research space."
        )

    available_outputs = tuple(
        item.name
        for item in research_space.outputs
    )

    selected_output = _select_option(
        requested=output,
        available=available_outputs,
        option_name="output",
        error_type=UnsupportedOutputError,
    )

    if selected_output is None:
        raise UnsupportedOutputError(
            f"Indicator {descriptor.id!r} "
            "does not declare any outputs."
        )

    selected_profile = _select_option(
        requested=profile,
        available=tuple(
            research_space.research_profiles
        ),
        option_name="profile",
        error_type=UnsupportedProfileError,
    )

    selected_observation_type = _select_option(
        requested=observation_type,
        available=tuple(
            research_space.observation_types
        ),
        option_name="observation_type",
        error_type=(
            UnsupportedObservationTypeError
        ),
    )

    selected_signal_rule_id = _select_option(
        requested=signal_rule_id,
        available=tuple(
            research_space.signal_rule_ids
        ),
        option_name="signal_rule_id",
        error_type=ResearchSpecificationError,
    )
    
    resolved_calculation_parameters = (
        _resolve_parameters(
            supplied=calculation_parameters,
            spaces=(
                research_space
                .calculation_parameters
            ),
            parameter_group="calculation",
        )
    )

    resolved_observation_parameters = (
        _resolve_parameters(
            supplied=observation_parameters,
            spaces=(
                research_space
                .observation_parameters
            ),
            parameter_group="observation",
        )
    )

    return ResearchSpecification.create(
        indicator=IndicatorReference(
            indicator_id=descriptor.id,
            indicator_version=descriptor.version,
        ),
        output=selected_output,
        profile=selected_profile,
        observation_type=(
            selected_observation_type
        ),
        signal_rule_id=(
            selected_signal_rule_id
        ),
        calculation_parameters=(
            resolved_calculation_parameters
        ),
        observation_parameters=(
            resolved_observation_parameters
        ),
    )


def create_default_research_specification(
    descriptor: IndicatorDescriptor,
) -> ResearchSpecification:
    return create_research_specification(
        descriptor
    )