from datetime import datetime, timezone

import pandas as pd

from src.application.indicator_market_signal_provider import (
    IndicatorMarketSignalProvider,
)
from src.application.indicator_research_execution_service import (
    IndicatorResearchExecutionService,
)
from src.application.mappers.indicator_specification_mapper import (
    IndicatorSpecificationMapper,
)
from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
    MarketPositionDirection,
)
from src.indicators.calculation_service import (
    IndicatorCalculationService,
)
from src.indicators.catalog import (
    IndicatorCatalog,
)
from src.indicators.implementations.williams_r import (
    INDICATOR,
)
from src.research.specification import (
    IndicatorReference,
    ResearchSpecification,
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


class WilliamsOversoldObservationService:
    def calculate(
        self,
        *,
        series,
        observation_type: str,
        parameters: dict[str, object],
    ) -> tuple[int, ...]:

        level = int(
            parameters.get(
                "oversold_level",
                -80,
            )
        )

        return tuple(
            1
            if value is not None
            and value <= level
            else 0
            for value in series.values
        )


def build_specification() -> MarketExperimentSpecification:
    return MarketExperimentSpecification(
        executor_type="market_backtest",
        question_title="Williams test",
        question_description="Test Williams indicator",
        hypothesis_title="Williams hypothesis",
        hypothesis_description="Oversold rebound",
        expected_result="Positive result",
        experiment_title="Williams experiment",
        experiment_description="Historical test",
        data_source="test",
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
            10,
            tzinfo=timezone.utc,
        ),
        entry_rule="williams",
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
            output="williams_r",
            profile="overbought_oversold",
            observation_type="level_cross",
            signal_rule_id="indicator_direction",
            calculation_parameters={
                "period": 3,
            },
            observation_parameters={
                "oversold_level": -80,
            },
        ),
    )


def test_indicator_market_signal_provider_with_real_williams() -> None:

    catalog = IndicatorCatalog(
        (
            INDICATOR,
        ),
    )

    signal_service = SignalGenerationService(
        SignalRuleRegistry(
            discover_signal_rules(),
        )
    )

    execution_service = (
        IndicatorResearchExecutionService(
            specification_mapper=(
                IndicatorSpecificationMapper()
            ),
            calculation_service=(
                IndicatorCalculationService(
                    catalog,
                )
            ),
            observation_service=(
                WilliamsOversoldObservationService()
            ),
            signal_service=signal_service,
        )
    )

    provider = IndicatorMarketSignalProvider(
        research_execution_service=execution_service,
    )

    data = pd.DataFrame(
        {
            "high": [
                10,
                11,
                12,
                13,
                14,
            ],
            "low": [
                5,
                6,
                7,
                8,
                9,
            ],
            "close": [
                6,
                7,
                8,
                9,
                10,
            ],
        }
    )

    result = provider.generate(
        data,
        build_specification(),
    )

    assert "AI_prediction" in result.columns

    assert len(result) == len(data)

    assert set(
        result["AI_prediction"].tolist()
    ).issubset(
        {
            -1,
            0,
            1,
        }
    )