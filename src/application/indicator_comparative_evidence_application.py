from __future__ import annotations

from src.application.indicator_comparative_evidence_service import (
    IndicatorComparativeEvidenceService,
)
from src.application.indicator_comparative_research_application import (
    IndicatorComparativeResearchApplication,
)
from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
)
from src.research.evidence import Evidence
from src.research.outcome_specification import (
    ForwardReturnSpecification,
)


class IndicatorComparativeEvidenceApplication:
    """
    Coordinates replicated comparative research for one hypothesis.

    Each market specification produces one independent research result.
    The resulting replications are aggregated into Evidence, not a
    Finding.
    """

    def __init__(
        self,
        *,
        research_application: (
            IndicatorComparativeResearchApplication
        ),
        evidence_service: (
            IndicatorComparativeEvidenceService
        ),
    ) -> None:
        if not isinstance(
            research_application,
            IndicatorComparativeResearchApplication,
        ):
            raise TypeError(
                "research_application must be an "
                "IndicatorComparativeResearchApplication"
            )

        if not isinstance(
            evidence_service,
            IndicatorComparativeEvidenceService,
        ):
            raise TypeError(
                "evidence_service must be an "
                "IndicatorComparativeEvidenceService"
            )

        self._research_application = (
            research_application
        )
        self._evidence_service = evidence_service

    def run(
        self,
        *,
        hypothesis_id: str,
        market_specifications: tuple[
            MarketExperimentSpecification,
            ...,
        ],
        indicator_id: str,
        outcome_specification: (
            ForwardReturnSpecification
        ),
        horizon: int,
    ) -> Evidence:
        normalized_hypothesis_id = (
            self._normalize_text(
                hypothesis_id,
                field_name="hypothesis_id",
            )
        )
        normalized_indicator_id = (
            self._normalize_text(
                indicator_id,
                field_name="indicator_id",
            )
        )

        if not isinstance(
            outcome_specification,
            ForwardReturnSpecification,
        ):
            raise TypeError(
                "outcome_specification must be a "
                "ForwardReturnSpecification"
            )

        normalized_horizon = (
            self._validate_horizon(horizon)
        )

        if (
            normalized_horizon
            not in outcome_specification.horizons
        ):
            raise ValueError(
                "horizon must be included in "
                "outcome_specification"
            )

        normalized_specifications = (
            self._validate_market_specifications(
                market_specifications
            )
        )

        results = tuple(
            self._research_application.run(
                market_specification=specification,
                indicator_id=(
                    normalized_indicator_id
                ),
                outcome_specification=(
                    outcome_specification
                ),
            )
            for specification
            in normalized_specifications
        )

        return self._evidence_service.evaluate(
            hypothesis_id=(
                normalized_hypothesis_id
            ),
            results=results,
            horizon=normalized_horizon,
        )

    @classmethod
    def _validate_market_specifications(
        cls,
        specifications: object,
    ) -> tuple[
        MarketExperimentSpecification,
        ...,
    ]:
        if not isinstance(specifications, tuple):
            raise TypeError(
                "market_specifications must be a tuple"
            )

        if not specifications:
            raise ValueError(
                "market_specifications must not be empty"
            )

        normalized: list[
            MarketExperimentSpecification
        ] = []

        for specification in specifications:
            if not isinstance(
                specification,
                MarketExperimentSpecification,
            ):
                raise TypeError(
                    "each market specification must be a "
                    "MarketExperimentSpecification"
                )

            normalized.append(specification)

        reference = normalized[0]

        for specification in normalized[1:]:
            if (
                specification.symbol
                != reference.symbol
            ):
                raise ValueError(
                    "market specifications must use "
                    "the same symbol"
                )

            if (
                specification.timeframe
                != reference.timeframe
            ):
                raise ValueError(
                    "market specifications must use "
                    "the same timeframe"
                )

        return tuple(normalized)

    @staticmethod
    def _validate_horizon(
        value: object,
    ) -> int:
        if (
            not isinstance(value, int)
            or isinstance(value, bool)
        ):
            raise TypeError(
                "horizon must be an integer"
            )

        if value < 1:
            raise ValueError(
                "horizon must be positive"
            )

        return value

    @staticmethod
    def _normalize_text(
        value: object,
        *,
        field_name: str,
    ) -> str:
        if not isinstance(value, str):
            raise TypeError(
                f"{field_name} must be a string"
            )

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                f"{field_name} must not be empty"
            )

        return normalized
