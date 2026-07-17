import json
from pathlib import Path
from typing import Any

import pandas as pd

from src.application.market_research_application import (
    build_market_research_application,
)
from src.cli.run_market_research_command import (
    RunMarketResearchCommand,
)

class FakeMarketDataProvider:
    def load(
        self,
        specification,
    ):
        return pd.DataFrame(
            {
                "Open": [100.0, 100.0, 103.0],
                "High": [100.0, 103.0, 103.0],
                "Low": [100.0, 102.0, 103.0],
                "Close": [100.0, 103.0, 103.0],
                "Volume": [1000, 1100, 1200],
            },
            index=pd.date_range(
                start="2024-01-01",
                periods=3,
                freq="D",
            ),
        )

class FakeMarketSignalProvider:
    """
    Adds deterministic signals expected by BacktestEngine.
    """

    def generate(
        self,
        data: pd.DataFrame,
        specification,
    ) -> pd.DataFrame:
        prepared = data.copy()

        prepared["AI_prediction"] = [
            1,
            1,
            0,
        ]

        return prepared


class InMemorySerializedResearchCycleStore:
    """
    Captures serialized cycles without filesystem persistence.
    """

    def __init__(self) -> None:
        self.saved_cycles: dict[
            str,
            dict[str, Any],
        ] = {}

    def save(
        self,
        result_id: str,
        serialized_cycle: dict[str, Any],
    ) -> None:
        self.saved_cycles[result_id] = serialized_cycle


def write_specification(
    path: Path,
) -> None:
    payload = {
        "executor_type": "market_backtest",
        "question_title": (
            "Can a JSON specification launch market research?"
        ),
        "question_description": (
            "Verify the complete CLI command execution boundary."
        ),
        "hypothesis_title": (
            "The command executes a reproducible market experiment"
        ),
        "hypothesis_description": (
            "A valid JSON specification should produce a research cycle."
        ),
        "expected_result": (
            "The backtest produces at least one profitable trade."
        ),
        "experiment_title": (
            "Run market research command experiment"
        ),
        "experiment_description": (
            "Execute deterministic market data through the application."
        ),
        "data_source": "test",
        "symbol": "BTCUSDT",
        "timeframe": "1H",
        "start_at": "2024-01-01T00:00:00+00:00",
        "end_at": "2024-02-01T00:00:00+00:00",
        "entry_rule": "test signal",
        "exit_rule": "execution policy",
        "direction": "LONG",
        "stop_loss_percent": 2.0,
        "take_profit_percent": 2.0,
        "max_holding_bars": 10,
        "commission_percent": 0.0,
        "slippage_percent": 0.0,
        "strategy_parameters": {
            "signal_type": "deterministic_test",
        },
        "tags": [
            "cli",
            "market-research",
        ],
    }

    path.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def test_run_market_research_command_executes_json_specification(
    tmp_path: Path,
) -> None:
    specification_path = tmp_path / "experiment.json"

    write_specification(
        specification_path,
    )

    store = InMemorySerializedResearchCycleStore()

    application = build_market_research_application(
        data_provider=FakeMarketDataProvider(),
        signal_provider=FakeMarketSignalProvider(),
        store=store,
    )

    command = RunMarketResearchCommand(
        run_market_research=application,
    )

    rendered = command.execute(
        specification_path,
    )

    parsed = json.loads(rendered)

    result_id = parsed["result"]["id"]

    assert parsed["result"]["success"] is True
    assert parsed["result"]["metrics"]["total_trades"] == 1
    assert parsed["result"]["metrics"]["net_profit"] > 0

    assert result_id in store.saved_cycles

    assert (
        store.saved_cycles[result_id]["cycle"]["result"]["id"]
        == result_id
    )


def test_run_market_research_command_supports_compact_json(
    tmp_path: Path,
) -> None:
    specification_path = tmp_path / "experiment.json"

    write_specification(
        specification_path,
    )

    application = build_market_research_application(
        data_provider=FakeMarketDataProvider(),
        signal_provider=FakeMarketSignalProvider(),
        store=InMemorySerializedResearchCycleStore(),
    )

    command = RunMarketResearchCommand(
        run_market_research=application,
    )

    rendered = command.execute(
        specification_path,
        indent=None,
    )

    assert "\n" not in rendered
    assert json.loads(rendered)["result"]["success"] is True


def test_run_market_research_command_reports_invalid_specification(
    tmp_path: Path,
) -> None:
    specification_path = tmp_path / "invalid.json"

    specification_path.write_text(
        '{"executor_type": "market_backtest"}',
        encoding="utf-8",
    )

    application = build_market_research_application(
        data_provider=FakeMarketDataProvider(),
        signal_provider=FakeMarketSignalProvider(),
        store=InMemorySerializedResearchCycleStore(),
    )

    command = RunMarketResearchCommand(
        run_market_research=application,
    )

    try:
        command.execute(
            specification_path,
        )
    except ValueError as error:
        assert "missing specification fields" in str(error)
    else:
        raise AssertionError(
            "Expected invalid specification to raise ValueError."
        )