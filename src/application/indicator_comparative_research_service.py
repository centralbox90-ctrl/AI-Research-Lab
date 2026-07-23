from __future__ import annotations

import pandas as pd

from src.application.indicator_comparative_research_design import (
    IndicatorComparativeResearchDesign,
)
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
        design: IndicatorComparativeResearchDesign,
        symbol: str,
        timeframe: str,
    ) -> ComparativeAnalysis:
        if not isinstance(
            design,
            IndicatorComparativeResearchDesign,
        ):
            raise TypeError(
                "design must be an "
                "IndicatorComparativeResearchDesign"
            )

        indicator_result = (
            self._research_execution_service.execute(
                data=data,
                specification=(
                    design.research_specification
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
                    design
                    .outcome_specification
                    .price_field
                ),
            )
        )

        return ComparativeAnalysisService().run(
            data=data,
            observations=observations,
            specification=(
                design.outcome_specification
            ),
        )
