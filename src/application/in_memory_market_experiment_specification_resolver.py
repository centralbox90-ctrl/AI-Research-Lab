from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType

from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
)
from src.research.research_planner import (
    CampaignExperimentSpecification,
)


class InMemoryMarketExperimentSpecificationResolver:
    """
    Resolves planned experiments through explicit registrations.

    Registrations are keyed by the deterministic identifier of a
    CampaignExperimentSpecification. Opaque campaign references are
    never parsed or interpreted by this resolver.
    """

    def __init__(
        self,
        registrations: Mapping[
            str,
            MarketExperimentSpecification,
        ],
    ) -> None:
        if not isinstance(registrations, Mapping):
            raise TypeError(
                "registrations must be a mapping"
            )

        if not registrations:
            raise ValueError(
                "registrations must not be empty"
            )

        normalized: dict[
            str,
            MarketExperimentSpecification,
        ] = {}

        for registration_id, specification in (
            registrations.items()
        ):
            if not isinstance(registration_id, str):
                raise TypeError(
                    "registration IDs must be strings"
                )

            normalized_id = registration_id.strip()

            if not normalized_id:
                raise ValueError(
                    "registration IDs must not be empty"
                )

            if not isinstance(
                specification,
                MarketExperimentSpecification,
            ):
                raise TypeError(
                    "registered values must be "
                    "MarketExperimentSpecification instances"
                )

            if normalized_id in normalized:
                raise ValueError(
                    "registration IDs must be unique "
                    "after normalization"
                )

            normalized[normalized_id] = specification

        self._registrations = MappingProxyType(
            normalized
        )

    @property
    def registered_ids(self) -> tuple[str, ...]:
        return tuple(
            sorted(self._registrations)
        )

    def resolve(
        self,
        planned_specification: CampaignExperimentSpecification,
    ) -> MarketExperimentSpecification:
        if not isinstance(
            planned_specification,
            CampaignExperimentSpecification,
        ):
            raise TypeError(
                "planned_specification must be a "
                "CampaignExperimentSpecification"
            )

        registration_id = planned_specification.id

        try:
            return self._registrations[
                registration_id
            ]
        except KeyError as error:
            raise ValueError(
                "no market experiment specification "
                "registered for planned experiment "
                f"{registration_id}"
            ) from error
