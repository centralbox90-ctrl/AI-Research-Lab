from src.application.market_research_application import (
    build_default_market_research_application,
)
from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
    MarketPositionDirection,
)
from datetime import datetime, timezone


def test_default_market_research_application_is_buildable():

    application = build_default_market_research_application()

    specification = MarketExperimentSpecification(
        executor_type="market_backtest",
        question_title="Test default application",
        question_description="Test",
        hypothesis_title="Market growth hypothesis",
        hypothesis_description="Test hypothesis",
        expected_result="Positive result",
        experiment_title="Default application experiment",
        experiment_description="Test execution",
        data_source="generated",
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
            2,
            1,
            tzinfo=timezone.utc,
        ),
        entry_rule="simple",
        exit_rule="simple",
        direction=MarketPositionDirection.LONG,
        stop_loss_percent=2.0,
        take_profit_percent=2.0,
        max_holding_bars=10,
    )

    result = application.execute(
        specification,
    )

    assert result.result is not None