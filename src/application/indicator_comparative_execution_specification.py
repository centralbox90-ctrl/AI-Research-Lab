from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256

from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
)
from src.research.outcome_specification import (
    ForwardReturnSpecification,
)
from src.research.specification import (
    ResearchSpecification,
)


@dataclass(frozen=True, slots=True)
class IndicatorComparativeExecutionSpecification:
    """
    Complete reproducible input of one comparative analysis execution.

    Statistical evaluation is intentionally excluded because it occurs
    after the technical experiment execution has succeeded.
    """

    market_specification: MarketExperimentSpecification
    research_specification: ResearchSpecification
    outcome_specification: ForwardReturnSpecification
    baseline: str = "unconditional"

    def __post_init__(self) -> None:
        if not isinstance(
            self.market_specification,
            MarketExperimentSpecification,
        ):
            raise TypeError(
                "market_specification must be a "
                "MarketExperimentSpecification"
            )

        if not isinstance(
            self.research_specification,
            ResearchSpecification,
        ):
            raise TypeError(
                "research_specification must be a "
                "ResearchSpecification"
            )

        if not isinstance(
            self.outcome_specification,
            ForwardReturnSpecification,
        ):
            raise TypeError(
                "outcome_specification must be a "
                "ForwardReturnSpecification"
            )

        if not isinstance(self.baseline, str):
            raise TypeError(
                "baseline must be a string"
            )

        baseline = self.baseline.strip()

        if baseline != "unconditional":
            raise ValueError(
                "baseline must be 'unconditional'"
            )

        object.__setattr__(
            self,
            "baseline",
            baseline,
        )

    def to_dict(self) -> dict[str, object]:
        market = self.market_specification

        return {
            "schema_version": 1,
            "execution_type": (
                "indicator_comparative_research"
            ),
            "market_data": {
                "data_source": (
                    market.data_source.strip()
                ),
                "symbol": market.symbol.strip(),
                "timeframe": market.timeframe.strip(),
                "start_at": self._serialize_datetime(
                    market.start_at
                ),
                "end_at": self._serialize_datetime(
                    market.end_at
                ),
            },
            "research_specification": (
                self.research_specification.to_dict()
            ),
            "outcome_specification": {
                "horizons": list(
                    self.outcome_specification.horizons
                ),
                "price_field": (
                    self.outcome_specification.price_field
                ),
            },
            "baseline": self.baseline,
        }

    @property
    def fingerprint(self) -> str:
        serialized = json.dumps(
            self.to_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )

        return sha256(
            serialized.encode("utf-8")
        ).hexdigest()

    @staticmethod
    def _serialize_datetime(
        value: datetime,
    ) -> str:
        if (
            value.tzinfo is not None
            and value.utcoffset() is not None
        ):
            return value.astimezone(
                timezone.utc
            ).isoformat()

        return value.isoformat()
