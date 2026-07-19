from datetime import UTC, datetime

import pandas as pd

from src.indicators.series import IndicatorSeries
from src.indicators.specification import IndicatorSpecification
from src.research.observations.indicator.provider import (
    IndicatorObservationProvider,
)
from src.research.observations.indicator.williams_r_definition import (
    WilliamsRObservationDefinition,
)
from src.research.observations.observation import Observation
from src.research.observations.pipeline import ObservationPipeline


class StubIndicator:
    def __init__(self) -> None:
        self.called = False

    def calculate(
        self,
        data: pd.DataFrame,
    ) -> IndicatorSeries:
        self.called = True

        return IndicatorSeries.create(
            specification=IndicatorSpecification(
                indicator_type="williams_r",
                version=1,
                parameters={
                    "period": 3,
                },
            ),
            timestamps=(
                datetime(
                    2026,
                    1,
                    1,
                    tzinfo=UTC,
                ),
            ),
            values=(
                None,
            ),
            warmup_bars=1,
        )


class StubProvider(
    IndicatorObservationProvider,
):
    def __init__(self) -> None:
        self.called = False

    def observe(
        self,
        series,
        definition,
    ):
        self.called = True

        return [
           Observation(
              id="1",
              definition_id=definition.id,
              symbol="BTCUSDT",
              timeframe="1h",
              timestamp=series.timestamps[0],
              bar_index=0,
              price=None,
           )
        ]


def make_definition():
    specification = IndicatorSpecification(
        indicator_type="williams_r",
        version=1,
        parameters={
            "period": 3,
        },
    )

    return WilliamsRObservationDefinition(
        id="definition",
        question_id="question",
        hypothesis_id="hypothesis",
        title="Williams",
        description="Williams crossing",
        observation_type="indicator",
        indicator=specification,
        level=-80,
        direction="cross_above",
    )


def test_pipeline_calls_indicator_and_provider():
    indicator = StubIndicator()
    provider = StubProvider()

    pipeline = ObservationPipeline(
        indicator,
        provider,
    )

    observations = pipeline.observe(
        pd.DataFrame(),
        make_definition(),
    )

    assert indicator.called
    assert provider.called
    assert len(observations) == 1
    assert observations[0].definition_id == "definition"