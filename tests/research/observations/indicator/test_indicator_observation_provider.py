from datetime import UTC, datetime

import pytest

from src.indicators.series import IndicatorSeries
from src.indicators.specification import IndicatorSpecification
from src.research.observations.indicator.definition import (
    IndicatorObservationDefinition,
)
from src.research.observations.indicator.provider import (
    IndicatorObservationProvider,
)


class StubIndicatorObservationProvider(
    IndicatorObservationProvider
):
    def observe(
        self,
        series: IndicatorSeries,
        definition: IndicatorObservationDefinition,
    ) -> list:
        return []


def test_indicator_provider_can_be_implemented_with_observe() -> None:
    provider = StubIndicatorObservationProvider()

    assert isinstance(provider, IndicatorObservationProvider)


def test_indicator_provider_rejects_find_without_series() -> None:
    provider = StubIndicatorObservationProvider()

    definition = IndicatorObservationDefinition(
        id="definition-1",
        question_id="question-1",
        hypothesis_id="hypothesis-1",
        title="Williams cross",
        description="Williams crosses above threshold",
        observation_type="indicator",
        indicator=IndicatorSpecification(
            indicator_type="williams_r",
            version=1,
            parameters={
                "period": 14,
            },
        ),
    )

    with pytest.raises(
        TypeError,
        match="requires an IndicatorSeries",
    ):
        provider.find(definition)