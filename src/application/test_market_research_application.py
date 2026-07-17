from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.application import (
    MarketExperimentSpecification,
    MarketPositionDirection,
    RunMarketResearch,
    build_market_research_application,
)
from src.storage import SqliteResearchCycleStore

class FakeMarketDataProvider:
    def load(
        self,
        specification,
    ) -> pd.DataFrame:
        index = pd.date_range(
            start="2024-01-01T00:00:00Z",
            periods=3,
            freq="h",
        )

        return pd.DataFrame(
            {
                "Open": [
                    100.0,
                    102.0,
                    103.0,
                ],
                "High": [
                    100.0,
                    103.0,
                    103.0,
                ],
                "Low": [
                    100.0,
                    102.0,
                    103.0,
                ],
                "Close": [
                    100.0,
                    103.0,
                    103.0,
                ],
                "Volume": [
                    1000,
                    1100,
                    1200,
                ],
            },
            index=index,
        )

class FakeMarketSignalProvider:
    def generate(
        self,
        data: pd.DataFrame,
        specification: MarketExperimentSpecification,
    ) -> pd.DataFrame:
        prepared_data = data.copy()

        prepared_data["AI_prediction"] = [
            1,
            1,
            0,
        ]

        return prepared_data


def build_specification() -> MarketExperimentSpecification:
    return MarketExperimentSpecification(
        executor_type="market_backtest",
        question_title="Does the registered rule produce profit?",
        question_description=(
            "Test the complete default market research application."
        ),
        hypothesis_title="The registered rule is profitable",
        hypothesis_description=(
            "The registered rule is expected to produce positive "
            "historical trade results."
        ),
        expected_result=(
            "Positive net profit with at least one completed trade."
        ),
        experiment_title="Default market application backtest",
        experiment_description=(
            "Run the default market research application graph."
        ),
        data_source="test_data",
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
        entry_rule="registered_entry_rule",
        exit_rule="registered_exit_rule",
        direction=MarketPositionDirection.LONG,
        stop_loss_percent=2.0,
        take_profit_percent=2.0,
        max_holding_bars=10,
    )


def test_build_market_research_application_creates_ready_use_case(
    tmp_path: Path,
) -> None:
    store = SqliteResearchCycleStore(
        db_path=tmp_path / "research_cycles.db",
    )

    application = build_market_research_application(
        data_provider=FakeMarketDataProvider(),
        signal_provider=FakeMarketSignalProvider(),
        store=store,
    )

    assert isinstance(
        application,
        RunMarketResearch,
    )

    cycle = application.execute(
        build_specification(),
    )

    assert cycle.result.success is True
    assert cycle.result.metrics["total_trades"] == 1
    assert cycle.result.metrics["net_profit"] == 2.0

    stored = store.get(cycle.result.id)

    assert stored is not None
    assert stored["cycle"]["result"]["id"] == cycle.result.id
    assert stored["cycle"]["result"]["success"] is True


def test_default_application_registers_market_backtest(
    tmp_path: Path,
) -> None:
    store = SqliteResearchCycleStore(
        db_path=tmp_path / "research_cycles.db",
    )

    application = build_market_research_application(
        data_provider=FakeMarketDataProvider(),
        signal_provider=FakeMarketSignalProvider(),
        store=store,
    )

    assert application.registry.list_executor_types() == [
        "market_backtest",
    ]