from __future__ import annotations

import json
from json import JSONDecodeError
from pathlib import Path
from typing import Any

from src.application.in_memory_market_experiment_specification_resolver import (
    InMemoryMarketExperimentSpecificationResolver,
)
from src.application.market_experiment_specification_loader import (
    MarketExperimentSpecificationLoader,
)
from src.research.research_planner import (
    ResearchCampaignPlan,
)


class MarketExperimentRegistrationLoader:
    """
    Loads a complete resolver registration set for one campaign plan.
    """

    SCHEMA_VERSION = 1

    _TOP_LEVEL_FIELDS = {
        "schema_version",
        "campaign_plan_id",
        "registrations",
    }

    _REGISTRATION_FIELDS = {
        "planned_experiment_id",
        "market_specification",
    }

    def __init__(
        self,
        specification_loader: (
            MarketExperimentSpecificationLoader | None
        ) = None,
    ) -> None:
        if (
            specification_loader is not None
            and not isinstance(
                specification_loader,
                MarketExperimentSpecificationLoader,
            )
        ):
            raise TypeError(
                "specification_loader must be a "
                "MarketExperimentSpecificationLoader or None"
            )

        self._specification_loader = (
            specification_loader
            or MarketExperimentSpecificationLoader()
        )

    def load(
        self,
        path: str | Path,
        *,
        plan: ResearchCampaignPlan,
    ) -> InMemoryMarketExperimentSpecificationResolver:
        registration_path = Path(path)

        try:
            source = registration_path.read_text(
                encoding="utf-8",
            )
        except OSError as error:
            raise ValueError(
                "unable to read campaign registration file: "
                f"{registration_path}"
            ) from error

        try:
            payload = json.loads(source)
        except JSONDecodeError as error:
            raise ValueError(
                "invalid campaign registration JSON: "
                f"{error.msg}"
            ) from error

        return self.from_dict(
            payload,
            plan=plan,
        )

    def from_dict(
        self,
        payload: Any,
        *,
        plan: ResearchCampaignPlan,
    ) -> InMemoryMarketExperimentSpecificationResolver:
        if not isinstance(plan, ResearchCampaignPlan):
            raise TypeError(
                "plan must be a ResearchCampaignPlan"
            )

        if not isinstance(payload, dict):
            raise ValueError(
                "campaign registration JSON "
                "must contain an object"
            )

        self._validate_fields(
            payload,
            expected=self._TOP_LEVEL_FIELDS,
            context="campaign registration",
        )

        schema_version = payload["schema_version"]

        if (
            not isinstance(schema_version, int)
            or isinstance(schema_version, bool)
            or schema_version != self.SCHEMA_VERSION
        ):
            raise ValueError(
                "schema_version must be 1"
            )

        campaign_plan_id = payload["campaign_plan_id"]

        if (
            not isinstance(campaign_plan_id, str)
            or not campaign_plan_id.strip()
        ):
            raise ValueError(
                "campaign_plan_id must be a "
                "non-empty string"
            )

        if campaign_plan_id.strip() != plan.id:
            raise ValueError(
                "campaign_plan_id must match "
                "the supplied research plan"
            )

        entries = payload["registrations"]

        if not isinstance(entries, list):
            raise ValueError(
                "registrations must be an array"
            )

        if not entries:
            raise ValueError(
                "registrations must not be empty"
            )

        planned_by_id = {
            specification.id: specification
            for specification
            in plan.experiment_specifications
        }
        registrations = {}

        for index, entry in enumerate(entries):
            context = f"registration {index}"

            if not isinstance(entry, dict):
                raise ValueError(
                    f"{context} must be an object"
                )

            self._validate_fields(
                entry,
                expected=self._REGISTRATION_FIELDS,
                context=context,
            )

            planned_experiment_id = entry[
                "planned_experiment_id"
            ]

            if (
                not isinstance(
                    planned_experiment_id,
                    str,
                )
                or not planned_experiment_id.strip()
            ):
                raise ValueError(
                    f"{context} planned_experiment_id "
                    "must be a non-empty string"
                )

            normalized_id = (
                planned_experiment_id.strip()
            )

            if normalized_id in registrations:
                raise ValueError(
                    "planned_experiment_id values "
                    "must be unique"
                )

            if normalized_id not in planned_by_id:
                raise ValueError(
                    "registration references an unknown "
                    f"planned experiment: {normalized_id}"
                )

            market_payload = entry[
                "market_specification"
            ]
            market_specification = (
                self._specification_loader.from_dict(
                    market_payload
                )
            )
            planned_specification = planned_by_id[
                normalized_id
            ]

            if (
                market_specification.symbol
                != planned_specification.instrument
            ):
                raise ValueError(
                    "registered market specification "
                    "symbol must match the planned instrument"
                )

            if (
                market_specification.timeframe
                != planned_specification.timeframe
            ):
                raise ValueError(
                    "registered market specification "
                    "timeframe must match the planned timeframe"
                )

            registrations[normalized_id] = (
                market_specification
            )

        missing_ids = sorted(
            set(planned_by_id) - set(registrations)
        )

        if missing_ids:
            raise ValueError(
                "missing planned experiment registrations: "
                + ", ".join(missing_ids)
            )

        return (
            InMemoryMarketExperimentSpecificationResolver(
                registrations
            )
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

        payload_fields = set(payload)

        missing_fields = sorted(
            expected - payload_fields
        )

        if missing_fields:
            raise ValueError(
                f"missing {context} fields: "
                + ", ".join(missing_fields)
            )

        unknown_fields = sorted(
            payload_fields - expected
        )

        if unknown_fields:
            raise ValueError(
                f"unknown {context} fields: "
                + ", ".join(unknown_fields)
            )
