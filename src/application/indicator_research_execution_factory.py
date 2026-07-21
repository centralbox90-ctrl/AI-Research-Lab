from __future__ import annotations

from src.application.indicator_research_execution_service import (
    IndicatorResearchExecutionService,
)
from src.application.mappers.indicator_specification_mapper import (
    IndicatorSpecificationMapper,
)
from src.application.observation_calculation_service import (
    ObservationCalculationService,
)
from src.application.observations.discovery import (
    discover_observations,
)
from src.indicators.calculation_service import (
    IndicatorCalculationService,
)
from src.indicators.catalog import (
    IndicatorCatalog,
)
from src.signals.discovery import (
    discover_signal_rules,
)
from src.signals.registry import (
    SignalRuleRegistry,
)
from src.signals.service import (
    SignalGenerationService,
)


class IndicatorResearchExecutionFactory:
    """
    Creates configured IndicatorResearchExecutionService.
    """

    def __init__(
        self,
        *,
        indicator_catalog: IndicatorCatalog,
    ) -> None:

        self._indicator_catalog = (
            indicator_catalog
        )

    def create(
        self,
    ) -> IndicatorResearchExecutionService:

        calculation_service = (
            IndicatorCalculationService(
                self._indicator_catalog,
            )
        )

        observation_service = (
            ObservationCalculationService(
                discover_observations(),
            )
        )

        signal_registry = SignalRuleRegistry(
            discover_signal_rules(),
        )

        signal_service = (
            SignalGenerationService(
                signal_registry,
            )
        )

        return IndicatorResearchExecutionService(
            specification_mapper=(
                IndicatorSpecificationMapper()
            ),
            calculation_service=(
                calculation_service
            ),
            observation_service=(
                observation_service
            ),
            signal_service=(
                signal_service
            ),
        )