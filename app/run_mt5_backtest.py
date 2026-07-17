from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from src.application.market_backtest_executor import (
    MarketBacktestExecutor,
)
from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
    MarketPositionDirection,
)
from src.application.mt5_market_data_provider import (
    Mt5MarketDataProvider,
)
from src.application.williams_market_signal_provider import (
    WilliamsMarketSignalProvider,
)
from src.research import Experiment


def make_json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            str(key): make_json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [
            make_json_safe(item)
            for item in value
        ]

    if hasattr(value, "item"):
        return value.item()

    return value


def build_specification() -> MarketExperimentSpecification:
    return MarketExperimentSpecification(
        executor_type="market_backtest",
        question_title=(
            "Can the existing research pipeline execute "
            "a backtest on real MT5 data?"
        ),
        question_description=(
            "Validate the complete market research pipeline using "
            "historical EURUSD H1 candles from RoboForex MT5."
        ),
        hypothesis_title=(
            "Real MT5 candles are compatible with the backtest pipeline"
        ),
        hypothesis_description=(
            "Mt5MarketDataProvider and SimpleMarketSignalProvider "
            "can produce a complete ExperimentResult without changing "
            "the existing MarketBacktestExecutor."
        ),
        expected_result=(
            "The executor returns trades, metrics, observations, "
            "and a conclusion."
        ),
        experiment_title="EURUSD H1 MT5 pipeline validation",
        experiment_description=(
            "Technical end-to-end validation using a simple "
            "close-direction signal. This is not a trading strategy."
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
        entry_rule=(
            "LONG when current Close is above previous Close; "
            "SHORT when current Close is below previous Close"
        ),
        exit_rule=(
            "Exit through stop loss, take profit, signal logic, "
            "or maximum holding bars as implemented by BacktestEngine"
        ),
        direction=MarketPositionDirection.LONG,
        stop_loss_percent=0.5,
        take_profit_percent=1.0,
        max_holding_bars=24,
        commission_percent=0.0,
        slippage_percent=0.0,
        strategy_parameters={
           "williams_period": 14,
           "williams_oversold": -80,
           "williams_overbought": -20,
          },
        tags=(
            "mt5",
            "roboforex",
            "eurusd",
            "h1",
            "pipeline-validation",
        ),
    )


def main() -> None:
    specification = build_specification()

    executor = MarketBacktestExecutor(
        specification=specification,
        data_provider=Mt5MarketDataProvider(),
        signal_provider=WilliamsMarketSignalProvider(),
    )

    experiment = Experiment(
        title=specification.experiment_title,
    )

    result = executor(experiment)

    exit_reasons = result.observations.get(
        "exit_reasons",
        [],
    )

    exit_reason_counts = {
        reason: exit_reasons.count(reason)
        for reason in sorted(set(exit_reasons))
    }

    output = {
        "experiment_id": str(result.experiment_id),
        "success": result.success,
        "metrics": make_json_safe(result.metrics),
        "observations_summary": {
            "profit_observations_count": len(
                result.observations.get(
                    "profit_percent",
                    [],
                )
            ),
            "exit_reason_counts": exit_reason_counts,
        },
        "conclusion": result.conclusion,
    }

    print()
    print("SUCCESS: MT5 backtest pipeline completed.")
    print()
    print(json.dumps(
        output,
        indent=2,
        ensure_ascii=False,
    ))


if __name__ == "__main__":
    main()