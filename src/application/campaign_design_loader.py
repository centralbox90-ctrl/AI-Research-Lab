from __future__ import annotations

import json
from json import JSONDecodeError
from pathlib import Path
from typing import Any

from src.research.campaign_design import (
    CampaignDesign,
)


class CampaignDesignLoader:
    """
    Loads and validates a reproducible CampaignDesign from JSON.
    """

    SCHEMA_VERSION = 1

    _DIMENSION_FIELDS = (
        "hypothesis_ids",
        "instruments",
        "timeframes",
        "data_periods",
        "indicator_configurations",
        "signal_rules",
        "execution_policies",
        "baselines",
    )

    _REQUIRED_FIELDS = {
        "schema_version",
        "question_id",
        *_DIMENSION_FIELDS,
        "validation_strategy",
        "evaluation_plan_ref",
        "provenance",
    }

    _OPTIONAL_FIELDS = {
        "id",
    }

    def load(
        self,
        path: str | Path,
    ) -> CampaignDesign:
        design_path = Path(path)

        try:
            source = design_path.read_text(
                encoding="utf-8",
            )
        except OSError as error:
            raise ValueError(
                "unable to read campaign design file: "
                f"{design_path}"
            ) from error

        try:
            payload = json.loads(source)
        except JSONDecodeError as error:
            raise ValueError(
                "invalid campaign design JSON: "
                f"{error.msg}"
            ) from error

        return self.from_dict(payload)

    def from_dict(
        self,
        payload: Any,
    ) -> CampaignDesign:
        if not isinstance(payload, dict):
            raise ValueError(
                "campaign design JSON must contain an object"
            )

        self._validate_fields(payload)

        schema_version = payload["schema_version"]

        if (
            not isinstance(schema_version, int)
            or isinstance(schema_version, bool)
            or schema_version != self.SCHEMA_VERSION
        ):
            raise ValueError(
                "schema_version must be 1"
            )

        dimensions: dict[str, tuple[object, ...]] = {}

        for field_name in self._DIMENSION_FIELDS:
            value = payload[field_name]

            if not isinstance(value, list):
                raise ValueError(
                    f"{field_name} must be an array"
                )

            dimensions[field_name] = tuple(value)

        provenance = payload["provenance"]

        if not isinstance(provenance, dict):
            raise ValueError(
                "provenance must be an object"
            )

        design = CampaignDesign(
            question_id=payload["question_id"],
            hypothesis_ids=dimensions[
                "hypothesis_ids"
            ],
            instruments=dimensions["instruments"],
            timeframes=dimensions["timeframes"],
            data_periods=dimensions["data_periods"],
            indicator_configurations=dimensions[
                "indicator_configurations"
            ],
            signal_rules=dimensions["signal_rules"],
            execution_policies=dimensions[
                "execution_policies"
            ],
            baselines=dimensions["baselines"],
            validation_strategy=payload[
                "validation_strategy"
            ],
            evaluation_plan_ref=payload[
                "evaluation_plan_ref"
            ],
            provenance=tuple(
                provenance.items()
            ),
        )

        if "id" in payload:
            supplied_id = payload["id"]

            if (
                not isinstance(supplied_id, str)
                or not supplied_id.strip()
            ):
                raise ValueError(
                    "id must be a non-empty string"
                )

            if supplied_id.strip() != design.id:
                raise ValueError(
                    "id must match the computed campaign design ID"
                )

        return design

    def _validate_fields(
        self,
        payload: dict[Any, Any],
    ) -> None:
        if any(
            not isinstance(key, str)
            for key in payload
        ):
            raise ValueError(
                "campaign design field names "
                "must be strings"
            )

        fields = set(payload)
        missing_fields = sorted(
            self._REQUIRED_FIELDS - fields
        )

        if missing_fields:
            raise ValueError(
                "missing campaign design fields: "
                + ", ".join(missing_fields)
            )

        supported_fields = (
            self._REQUIRED_FIELDS
            | self._OPTIONAL_FIELDS
        )
        unknown_fields = sorted(
            fields - supported_fields
        )

        if unknown_fields:
            raise ValueError(
                "unknown campaign design fields: "
                + ", ".join(unknown_fields)
            )
