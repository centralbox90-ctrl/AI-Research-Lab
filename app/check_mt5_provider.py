from datetime import datetime, timezone

from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
    MarketPositionDirection,
)
from src.application.mt5_market_data_provider import (
    Mt5MarketDataProvider,
)


def main() -> None:
    specification = MarketExperimentSpecification(
        executor_type="market_backtest",
        question_title="MT5 provider integration check",
        question_description=(
            "Can the project load real EURUSD H1 candles "
            "from RoboForex MT5?"
        ),
        hypothesis_title="MT5 historical data is compatible",
        hypothesis_description=(
            "The MT5 adapter returns the same internal DataFrame "
            "shape expected by the existing backtest pipeline."
        ),
        expected_result=(
            "A non-empty validated DataFrame with OHLCV columns."
        ),
        experiment_title="EURUSD H1 MT5 provider test",
        experiment_description=(
            "Load real historical EURUSD H1 candles from MT5."
        ),
        data_source="mt5",
        symbol="EURUSD",
        timeframe="H1",
        start_at=datetime(
            2026,
            1,
            19,
            0,
            0,
            tzinfo=timezone.utc,
        ),
        end_at=datetime(
            2026,
            7,
            16,
            8,
            0,
            tzinfo=timezone.utc,
        ),
        entry_rule="integration_test_only",
        exit_rule="integration_test_only",
        direction=MarketPositionDirection.LONG,
        stop_loss_percent=1.0,
        take_profit_percent=2.0,
        max_holding_bars=24,
        commission_percent=0.0,
        slippage_percent=0.0,
        strategy_parameters={},
        tags=("mt5", "integration"),
    )

    provider = Mt5MarketDataProvider()
    data = provider.load(specification)

    print()
    print("SUCCESS: Mt5MarketDataProvider loaded data.")
    print()
    print("Rows:", len(data))
    print("Columns:", list(data.columns))
    print("Index timezone:", data.index.tz)
    print("First timestamp:", data.index[0])
    print("Last timestamp:", data.index[-1])

    print()
    print("First row:")
    print(data.iloc[0])

    print()
    print("Last row:")
    print(data.iloc[-1])

    print()
    print("Provenance:")
    print(data.attrs.get("provenance"))


if __name__ == "__main__":
    main()