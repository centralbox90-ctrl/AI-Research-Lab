from datetime import datetime, timezone

import pandas as pd

from src.application import (
    MarketExperimentSpecification,
    MarketPositionDirection,
    MarketSignalProvider,
)


class MarketSignalProviderImplementation:
    def generate(
        self,
        data: pd.DataFrame,
        specification: MarketExperimentSpecification,
    ) -> pd.DataFrame:
        result = data.copy()

        result["AI_prediction"] = [
            1,
            1,
            0,
        ]

        return result


def build_specification() -> MarketExperimentSpecification:
    return MarketExperimentSpecification(
        executor_type="market_backtest",
        question_title="Does the rule generate profitable signals?",
        question_description=(
            "Test a registered market signal rule on historical data."
        ),
        hypothesis_title="The registered signal rule is profitable",
        hypothesis_description=(
            "The registered entry and exit rules are expected to "
            "produce positive historical trade returns."
        ),
        expected_result=(
            "Positive net profit with a non-zero number of trades."
        ),
        experiment_title="Registered signal rule backtest",
        experiment_description=(
            "Generate controlled signals and execute a historical "
            "market backtest."
        ),
        data_source="historical_csv",
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
            12,
            31,
            tzinfo=timezone.utc,
        ),
        entry_rule="registered_entry_rule",
        exit_rule="registered_exit_rule",
        direction=MarketPositionDirection.LONG,
        stop_loss_percent=1.0,
        take_profit_percent=2.0,
        max_holding_bars=24,
    )


def test_market_signal_provider_defines_signal_boundary() -> None:
    source_data = pd.DataFrame(
        {
            "Close": [
                100.0,
                105.0,
                110.0,
            ],
            "High": [
                101.0,
                106.0,
                111.0,
            ],
            "Low": [
                99.0,
                104.0,
                109.0,
            ],
        }
    )

    provider: MarketSignalProvider = (
        MarketSignalProviderImplementation()
    )

    result = provider.generate(
        data=source_data,
        specification=build_specification(),
    )

    assert result is not source_data
    assert "AI_prediction" not in source_data.columns

    assert result["AI_prediction"].tolist() == [
        1,
        1,
        0,
    ]

    assert result["Close"].tolist() == [
        100.0,
        105.0,
        110.0,
    ]