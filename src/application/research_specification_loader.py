from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from src.research.specification import (
    IndicatorReference,
    ResearchSpecification,
)


class ResearchSpecificationLoader:
    """Load a strict indicator research specification."""

    _FIELDS = {
        "indicator",
        "output",
        "profile",
        "observation_type",
        "signal_rule_id",
        "calculation_parameters",
        "observation_parameters",
    }

    _INDICATOR_FIELDS = {
        "id",
        "version",
    }

    def from_dict(
        self,
        payload: Any,
    ) -> ResearchSpecification:
        if not isinstance(payload, dict):
            raise ValueError(
                "research_specification must be an object"
            )

        self._validate_fields(
            payload,
            expected=self._FIELDS,
            context="research_specification",
        )

        indicator = payload["indicator"]

        if not isinstance(indicator, dict):
            raise ValueError(
                "research_specification indicator "
                "must be an object"
            )

        self._validate_fields(
            indicator,
            expected=self._INDICATOR_FIELDS,
            context="research_specification indicator",
        )

        calculation_parameters = payload[
            "calculation_parameters"
        ]

        observation_parameters = payload[
            "observation_parameters"
        ]

        if not isinstance(
            calculation_parameters,
            Mapping,
        ):
            raise ValueError(
                "research_specification "
                "calculation_parameters "
                "must be an object"
            )

        if not isinstance(
            observation_parameters,
            Mapping,
        ):
            raise ValueError(
                "research_specification "
                "observation_parameters "
                "must be an object"
            )

        return ResearchSpecification.create(
            indicator=IndicatorReference(
                indicator_id=indicator["id"],
                indicator_version=indicator["version"],
            ),
            output=payload["output"],
            profile=payload["profile"],
            observation_type=payload[
                "observation_type"
            ],
            signal_rule_id=payload["signal_rule_id"],
            calculation_parameters=dict(
                calculation_parameters
            ),
            observation_parameters=dict(
                observation_parameters
            ),
        )

    @staticmethod
    def _validate_fields(
        payload: dict[Any, Any],
        *,
        expected: set[str],
        context: str,
    ) -> None:
        if any(
            not isinstance(key, str)
            for key in payload
        ):
            raise ValueError(
                f"{context} field names must be strings"
            )

        fields = set(payload)
        missing = sorted(expected - fields)

        if missing:
            raise ValueError(
                f"missing {context} fields: "
                + ", ".join(missing)
            )

        unknown = sorted(fields - expected)

        if unknown:
            raise ValueError(
                f"unknown {context} fields: "
                + ", ".join(unknown)
            )
