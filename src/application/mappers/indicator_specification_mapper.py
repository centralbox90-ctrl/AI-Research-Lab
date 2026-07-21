from __future__ import annotations

from src.indicators.specification import (
    IndicatorSpecification,
)
from src.research.specification import (
    ResearchSpecification,
)


class IndicatorSpecificationMapper:
    """Преобразует research specification в calculation specification."""

    def map(
        self,
        specification: ResearchSpecification,
    ) -> IndicatorSpecification:
        return IndicatorSpecification(
            indicator_type=(
                specification.indicator.indicator_id
            ),
            version=(
                specification.indicator.indicator_version
            ),
            parameters=(
                specification.calculation_parameter_values
            ),
        )