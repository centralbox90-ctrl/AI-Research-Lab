from datetime import datetime, timezone

import pandas as pd

from src.application.indicator_market_signal_provider import (
    IndicatorMarketSignalProvider,
)
from src.application.indicator_research_execution_service import (
    IndicatorResearchExecutionService,
)
from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
    MarketPositionDirection,
)
from src.indicators.series import IndicatorSeries
from src.indicators.specification import (
    IndicatorSpecification,
)
from src.research.specification import (
    IndicatorReference,
    ResearchSpecification,
)
from src.signals.signal import (
    MarketSignal,
    MarketSignalDirection,
)


class FakeSpecificationMapper:

    def map(
        self,
        specification: ResearchSpecification,
    ) -> IndicatorSpecification:

        return IndicatorSpecification(
            indicator_type="williams_r",
            version=1,
            parameters={},
        )


class FakeCalculationService:

    def calculate(
        self,
        data: pd.DataFrame,
        specification: IndicatorSpecification,
    ) -> IndicatorSeries:

        timestamps = tuple(
            datetime(
                2024,
                1,
                day,
                tzinfo=timezone.utc,
            )
            for day in (
                1,
                2,
                3,
            )
        )

        return IndicatorSeries.create(
            specification=specification,
            timestamps=timestamps,
            values=(
                -90.0,
                -70.0,
                -20.0,
            ),
            warmup_bars=0,
        )


class FakeObservationService:

    def calculate(
        self,
        *,
        series: IndicatorSeries,
        observation_type: str,
        parameters: dict[str, object],
    ) -> tuple[int, ...]:

        return (
            1,
            0,
            -1,
        )


class FakeSignalService:

    def generate(
        self,
        *,
        rule_id: str,
        series: IndicatorSeries,
        observations: tuple[int, ...],
    ) -> tuple[MarketSignal, ...]:

        mapping = {
            1: MarketSignalDirection.LONG,
            0: MarketSignalDirection.NEUTRAL,
            -1: MarketSignalDirection.SHORT,
        }

        return tuple(
            MarketSignal(
                value=mapping[value],
            )
            for value in observations
        )


def build_specification():

    return MarketExperimentSpecification(
        executor_type="market_backtest",
        question_title="Question",
        question_description="Description",
        hypothesis_title="Hypothesis",
        hypothesis_description="Description",
        expected_result="Expected",
        experiment_title="Experiment",
        experiment_description="Description",
        data_source="historical",
        symbol="BTCUSDT",
        timeframe="1h",
        start_at=datetime(
            2024,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        end_at=datetime(
            2024,
            1,
            4,
            tzinfo=timezone.utc,
        ),
        entry_rule="entry",
        exit_rule="exit",
        direction=MarketPositionDirection.LONG,
        stop_loss_percent=1.0,
        take_profit_percent=2.0,
        max_holding_bars=10,
        research_specification=ResearchSpecification.create(
            indicator=IndicatorReference(
                indicator_id="williams_r",
                indicator_version=1,
            ),
            output="value",
            profile=None,
            observation_type="oversold",
            signal_rule_id="indicator_direction",
            calculation_parameters={},
            observation_parameters={},
        ),
    )


def test_generate_adds_ai_prediction_column():

    execution_service = (
        IndicatorResearchExecutionService(
            specification_mapper=(
                FakeSpecificationMapper()
            ),
            calculation_service=(
                FakeCalculationService()
            ),
            observation_service=(
                FakeObservationService()
            ),
            signal_service=(
                FakeSignalService()
            ),
        )
    )

    provider = IndicatorMarketSignalProvider(
        research_execution_service=execution_service,
    )

    data = pd.DataFrame(
        {
            "close": [
                1.0,
                2.0,
                3.0,
            ],
        }
    )

    result = provider.generate(
        data,
        build_specification(),
    )

    assert "AI_prediction" in result.columns

    assert result["AI_prediction"].tolist() == [
        1,
        0,
        -1,
    ]

    assert "AI_prediction" not in data.columns