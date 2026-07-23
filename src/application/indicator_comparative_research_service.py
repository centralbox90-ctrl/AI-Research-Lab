from __future__ import annotations

import pandas as pd

from src.application.indicator_research_execution_service import (
    IndicatorResearchExecutionService,
)
from src.application.observation_materialization_service import (
    ObservationMaterializationService,
)
from src.research.comparative_analysis import (
    ComparativeAnalysis,
)
from src.research.comparative_analysis_service import (
    ComparativeAnalysisService,
)
from src.research.outcome_specification import (
    ForwardReturnSpecification,
)
from src.research.specification import (
    ResearchSpecification,
)


class IndicatorComparativeResearchService:
    """
    Runs indicator observations through comparative outcome analysis.
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

    def run(
        self,
        *,
        data: pd.DataFrame,
        research_specification: ResearchSpecification,
        outcome_specification: ForwardReturnSpecification,
        symbol: str,
        timeframe: str,
    ) -> ComparativeAnalysis:
        indicator_result = (
            self._research_execution_service.execute(
                data=data,
                specification=(
                    research_specification
                ),
            )
        )

        observations = (
            ObservationMaterializationService()
            .materialize(
                data=data,
                result=indicator_result,
                symbol=symbol,
                timeframe=timeframe,
                price_field=(
                    outcome_specification.price_field
                ),
            )
        )

        return ComparativeAnalysisService().run(
            data=data,
            observations=observations,
            specification=outcome_specification,
        )
