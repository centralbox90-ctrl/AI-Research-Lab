from dataclasses import dataclass

from src.indicators.specification import IndicatorSpecification
from src.research.observations.definition import ObservationDefinition


@dataclass(frozen=True, slots=True)
class IndicatorObservationDefinition(ObservationDefinition):
    """
    ObservationDefinition, основанное на значениях индикатора.

    Определяет:
    - какой индикатор использовать;
    - какое условие искать.
    """

    indicator: IndicatorSpecification