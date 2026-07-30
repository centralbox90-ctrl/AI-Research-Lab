from __future__ import annotations

import json
from io import StringIO
from pathlib import Path

from src.cli.main import main


def write_specification(
    path: Path,
) -> None:
    payload = {
        "executor_type": "market_backtest",
        "question_title": (
            "Can production market research be traced?"
        ),
        "question_description": (
            "Verify the complete persisted production lifecycle."
        ),
        "hypothesis_title": (
            "A market experiment produces traceable artifacts"
        ),
        "hypothesis_description": (
            "One production run should align its result, "
            "execution history, and artifact envelope."
        ),
        "expected_result": (
            "The run completes and preserves reproducible identity."
        ),
        "experiment_title": (
            "Production lifecycle acceptance experiment"
        ),
        "experiment_description": (
            "Run deterministic generated market data "
            "through the complete CLI boundary."
        ),
        "data_source": "generated",
        "symbol": "BTCUSDT",
        "timeframe": "1h",
        "start_at": "2024-01-01T00:00:00+00:00",
        "end_at": "2024-02-01T00:00:00+00:00",
        "entry_rule": "positive close movement",
        "exit_rule": "execution policy",
        "direction": "LONG",
        "stop_loss_percent": 2.0,
        "take_profit_percent": 2.0,
        "max_holding_bars": 10,
        "commission_percent": 0.0,
        "slippage_percent": 0.0,
        "strategy_parameters": {
            "signal_type": "generated_movement",
        },
        "tags": [
            "production-lifecycle",
            "acceptance",
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


def run_cli(
    database_path: Path,
    *arguments: str,
) -> dict[str, object]:
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        [
            "--database",
            str(database_path),
            *arguments,
        ],
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 0, stderr.getvalue()
    assert stderr.getvalue() == ""

    return json.loads(
        stdout.getvalue()
    )


def test_market_research_production_lifecycle(
    tmp_path: Path,
) -> None:
    database_path = (
        tmp_path / "research-cycles.db"
    )
    specification_path = (
        tmp_path / "market-experiment.json"
    )

    write_specification(
        specification_path
    )

    cycle = run_cli(
        database_path,
        "run-research",
        "--spec",
        str(specification_path),
        "--compact",
    )
    result_id = cycle["result"]["id"]

    listing = run_cli(
        database_path,
        "list-experiment-executions",
        "--compact",
    )

    assert listing["schema_version"] == 1
    assert listing["execution_count"] == 1

    execution_id = listing[
        "execution_ids"
    ][0]

    history = run_cli(
        database_path,
        "get-experiment-execution-history",
        execution_id,
        "--compact",
    )

    assert history["schema_version"] == 1
    assert history["execution_id"] == execution_id
    assert history["snapshot_count"] == 3
    assert [
        snapshot["status"]
        for snapshot in history["snapshots"]
    ] == [
        "PENDING",
        "RUNNING",
        "SUCCEEDED",
    ]

    terminal_execution = history[
        "snapshots"
    ][-1]

    assert terminal_execution[
        "result_id"
    ] == result_id

    artifact = run_cli(
        database_path,
        "get-research-artifact",
        result_id,
        "--compact",
    )

    assert artifact["schema_version"] == 1
    assert artifact["artifact_type"] == (
        "market_research_cycle"
    )
    assert artifact["payload"]["cycle"][
        "result"
    ]["id"] == result_id

    source_references = {
        reference["reference_type"]: (
            reference["reference_id"]
        )
        for reference
        in artifact["source_references"]
    }

    assert source_references[
        "experiment_execution"
    ] == execution_id
    assert source_references[
        "experiment_result"
    ] == result_id
    assert artifact["correlation_id"] == (
        terminal_execution["correlation_id"]
    )
    assert artifact["provenance"][
        "specification_fingerprint"
    ] == terminal_execution[
        "specification_fingerprint"
    ]
    assert artifact["provenance"][
        "environment_fingerprint"
    ] == terminal_execution[
        "environment_fingerprint"
    ]
