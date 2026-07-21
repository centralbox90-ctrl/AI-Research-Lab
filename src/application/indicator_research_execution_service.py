from __future__ import annotations

import pandas as pd

from src.application.indicator_research_result import (
    IndicatorResearchResult,
)
from src.application.mappers.indicator_specification_mapper import (
    IndicatorSpecificationMapper,
)
from src.application.observation_calculation_service import (
    ObservationCalculationService,
)
from src.indicators.calculation_service import (
    IndicatorCalculationService,
)
from src.research.specification import (
    ResearchSpecification,
)
from src.signals.result import (
    MarketSignalResult,
)
from src.signals.service import (
    SignalGenerationService,
)


class IndicatorResearchExecutionService:
    """
    Executes indicator research specification.

    Pipeline:

        ResearchSpecification
            ↓
        IndicatorSpecification
            ↓
        IndicatorSeries
            ↓
        ObservationCalculationService
            ↓
        SignalGenerationService
            ↓
        MarketSignalResult
    """

    def __init__(
        self,
        *,
        specification_mapper: IndicatorSpecificationMapper,
        calculation_service: IndicatorCalculationService,
        observation_service: ObservationCalculationService,
        signal_service: SignalGenerationService,
    ) -> None:

        self._mapper = specification_mapper
        self._calculation_service = calculation_service
        self._observation_service = observation_service
        self._signal_service = signal_service

    def execute(
        self,
        *,
        data: pd.DataFrame,
        specification: ResearchSpecification,
    ) -> IndicatorResearchResult:

        indicator_specification = (
            self._mapper.map(
                specification,
            )
        )

        series = (
            self._calculation_service.calculate(
                data,
                indicator_specification,
            )
        )

        observations = (
            self._observation_service.calculate(
                series=series,
                observation_type=(
                    specification.observation_type
                ),
                parameters=(
                    specification
                    .observation_parameter_values
                ),
            )
        )

        signals = (
            self._signal_service.generate(
                rule_id=(
                    specification.signal_rule_id
                ),
                series=series,
                observations=observations,
            )
        )

        signal_result = MarketSignalResult(
            signals=signals,
            metadata={
                "observation_type": (
                    specification.observation_type
                ),
                "indicator": (
                    specification
                    .indicator
                    .indicator_id
                ),
                "signal_rule": (
                    specification.signal_rule_id
                ),
            },
        )

        return IndicatorResearchResult(
            research_specification=specification,
            series=series,
            signal_result=signal_result,
        )