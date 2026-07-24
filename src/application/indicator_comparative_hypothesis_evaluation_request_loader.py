from __future__ import annotations

import json
from dataclasses import dataclass
from json import JSONDecodeError
from pathlib import Path
from typing import Any

from src.application.indicator_comparative_hypothesis_evaluation_application import (
    IndicatorComparativeFindingRequest,
)
from src.application.market_experiment_specification_loader import (
    MarketExperimentSpecificationLoader,
)
from src.research.finding_evaluator import (
    FindingEvaluator,
)
from src.research.outcome_specification import (
    ForwardReturnSpecification,
)


@dataclass(frozen=True, slots=True)
class IndicatorComparativeHypothesisEvaluationRequest:
    """
    Typed input for one comparative hypothesis evaluation run.
    """

    hypothesis_id: str
    requests: tuple[
        IndicatorComparativeFindingRequest,
        ...,
    ]

    def __post_init__(self) -> None:
        if not isinstance(self.hypothesis_id, str):
            raise TypeError(
                "hypothesis_id must be a string"
            )

        normalized_hypothesis_id = (
            self.hypothesis_id.strip()
        )

        if not normalized_hypothesis_id:
            raise ValueError(
                "hypothesis_id must not be empty"
            )

        if not isinstance(self.requests, tuple):
            raise TypeError(
                "requests must be a tuple"
            )

        if not self.requests:
            raise ValueError(
                "requests must not be empty"
            )

        if any(
            not isinstance(
                request,
                IndicatorComparativeFindingRequest,
            )
            for request in self.requests
        ):
            raise TypeError(
                "each request must be an "
                "IndicatorComparativeFindingRequest"
            )

        object.__setattr__(
            self,
            "hypothesis_id",
            normalized_hypothesis_id,
        )


class IndicatorComparativeHypothesisEvaluationRequestLoader:
    """
    Loads the complete comparative evaluation request from JSON.
    """

    _REQUIRED_FIELDS = {
        "hypothesis_id",
        "requests",
    }
    _REQUEST_REQUIRED_FIELDS = {
        "market_specifications",
        "indicator_id",
        "outcome_specification",
        "horizon",
        "statement",
        "applicable_markets",
    }
    _REQUEST_OPTIONAL_FIELDS = {
        "analysis_pipeline_version",
    }
    _OUTCOME_REQUIRED_FIELDS = {
        "horizons",
    }
    _OUTCOME_OPTIONAL_FIELDS = {
        "price_field",
    }

    def __init__(
        self,
        market_specification_loader: (
            MarketExperimentSpecificationLoader | None
        ) = None,
    ) -> None:
        self._market_specification_loader = (
            market_specification_loader
            or MarketExperimentSpecificationLoader()
        )

    def load(
        self,
        path: str | Path,
    ) -> IndicatorComparativeHypothesisEvaluationRequest:
        request_path = Path(path)

        try:
            source = request_path.read_text(
                encoding="utf-8",
            )
        except OSError as error:
            raise ValueError(
                "unable to read comparative evaluation "
                f"request file: {request_path}"
            ) from error

        try:
            payload = json.loads(source)
        except JSONDecodeError as error:
            raise ValueError(
                "invalid comparative evaluation JSON: "
                f"{error.msg}"
            ) from error

        return self.from_dict(payload)

    def from_dict(
        self,
        payload: Any,
    ) -> IndicatorComparativeHypothesisEvaluationRequest:
        if not isinstance(payload, dict):
            raise ValueError(
                "comparative evaluation JSON must "
                "contain an object"
            )

        self._validate_fields(
            payload,
            required=self._REQUIRED_FIELDS,
            optional=set(),
            label="comparative evaluation request",
        )

        requests = payload["requests"]

        if not isinstance(requests, list):
            raise ValueError(
                "requests must be an array"
            )

        if not requests:
            raise ValueError(
                "requests must not be empty"
            )

        parsed_requests = tuple(
            self._parse_request(
                request,
                index=index,
            )
            for index, request in enumerate(requests)
        )

        try:
            return (
                IndicatorComparativeHypothesisEvaluationRequest(
                    hypothesis_id=payload["hypothesis_id"],
                    requests=parsed_requests,
                )
            )
        except (TypeError, ValueError) as error:
            raise ValueError(
                "invalid comparative evaluation request: "
                f"{error}"
            ) from error

    def _parse_request(
        self,
        payload: Any,
        *,
        index: int,
    ) -> IndicatorComparativeFindingRequest:
        label = f"requests[{index}]"

        if not isinstance(payload, dict):
            raise ValueError(
                f"{label} must be an object"
            )

        self._validate_fields(
            payload,
            required=self._REQUEST_REQUIRED_FIELDS,
            optional=self._REQUEST_OPTIONAL_FIELDS,
            label=label,
        )

        market_specifications = payload[
            "market_specifications"
        ]

        if not isinstance(market_specifications, list):
            raise ValueError(
                f"{label}.market_specifications "
                "must be an array"
            )

        if not market_specifications:
            raise ValueError(
                f"{label}.market_specifications "
                "must not be empty"
            )

        outcome_payload = payload[
            "outcome_specification"
        ]

        if not isinstance(outcome_payload, dict):
            raise ValueError(
                f"{label}.outcome_specification "
                "must be an object"
            )

        self._validate_fields(
            outcome_payload,
            required=self._OUTCOME_REQUIRED_FIELDS,
            optional=self._OUTCOME_OPTIONAL_FIELDS,
            label=f"{label}.outcome_specification",
        )

        horizons = outcome_payload["horizons"]

        if not isinstance(horizons, list):
            raise ValueError(
                f"{label}.outcome_specification.horizons "
                "must be an array"
            )

        applicable_markets = payload[
            "applicable_markets"
        ]

        if not isinstance(applicable_markets, list):
            raise ValueError(
                f"{label}.applicable_markets "
                "must be an array"
            )

        try:
            specifications = tuple(
                self._market_specification_loader.from_dict(
                    specification
                )
                for specification in market_specifications
            )
            outcome_specification = (
                ForwardReturnSpecification(
                    horizons=tuple(horizons),
                    price_field=outcome_payload.get(
                        "price_field",
                        "close",
                    ),
                )
            )

            return IndicatorComparativeFindingRequest(
                market_specifications=specifications,
                indicator_id=payload["indicator_id"],
                outcome_specification=(
                    outcome_specification
                ),
                horizon=payload["horizon"],
                statement=payload["statement"],
                applicable_markets=tuple(
                    applicable_markets
                ),
                analysis_pipeline_version=payload.get(
                    "analysis_pipeline_version",
                    FindingEvaluator.DEFAULT_PIPELINE_VERSION,
                ),
            )
        except (TypeError, ValueError) as error:
            raise ValueError(
                f"invalid {label}: {error}"
            ) from error

    @staticmethod
    def _validate_fields(
        payload: dict[str, Any],
        *,
        required: set[str],
        optional: set[str],
        label: str,
    ) -> None:
        missing_fields = sorted(
            required - payload.keys()
        )

        if missing_fields:
            raise ValueError(
                f"{label} missing fields: "
                + ", ".join(missing_fields)
            )

        supported_fields = required | optional
        unknown_fields = sorted(
            payload.keys() - supported_fields
        )

        if unknown_fields:
            raise ValueError(
                f"{label} unknown fields: "
                + ", ".join(unknown_fields)
            )