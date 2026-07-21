from __future__ import annotations

import pandas as pd

from src.application.indicator_research_execution_service import (
    IndicatorResearchExecutionService,
)
from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
)
from src.application.market_signal_provider import (
    MarketSignalProvider,
)


class IndicatorMarketSignalProvider(
    MarketSignalProvider,
):
    """
    Converts indicator research results into
    AI_prediction column.

    Responsibilities:

        Market Data
            +
        MarketExperimentSpecification
            |
            v
        IndicatorResearchExecutionService
            |
            v
        MarketSignalResult
            |
            v
        AI_prediction
    """

    def __init__(
        self,
        *,
        research_execution_service: (
            IndicatorResearchExecutionService
        ),
    ) -> None:

        self._research_execution_service = (
            research_execution_service
        )

    def generate(
        self,
        data: pd.DataFrame,
        specification: MarketExperimentSpecification,
    ) -> pd.DataFrame:

        if not isinstance(
            data,
            pd.DataFrame,
        ):
            raise TypeError(
                "data must be a pandas DataFrame"
            )

        if not isinstance(
            specification,
            MarketExperimentSpecification,
        ):
            raise TypeError(
                "specification must be a "
                "MarketExperimentSpecification"
            )

        research_specification = (
            specification.research_specification
        )

        if research_specification is None:
            raise ValueError(
                "research_specification is required"
            )

        research_result = (
            self._research_execution_service.execute(
                data=data,
                specification=(
                    research_specification
                ),
            )
        )

        predictions = tuple(
            int(signal.value)
            for signal in (
                research_result
                .signal_result
                .signals
            )
        )

        if len(predictions) != len(data):
            raise ValueError(
                "Generated signal count must match "
                "market data row count"
            )

        result = data.copy(
            deep=True,
        )

        result["AI_prediction"] = predictions

        return result