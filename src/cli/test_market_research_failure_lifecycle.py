from __future__ import annotations

import json
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path

import pandas as pd
import pytest

from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
    MarketPositionDirection,
)
from src.application.market_research_application import (
    build_market_research_application,
)
from src.cli.main import main
from src.storage import (
    SqliteExperimentExecutionRecorder,
    SqliteResearchCycleStore,
)


class DeterministicMarketDataProvider:
    def load(
        self,
        specification: MarketExperimentSpecification,
    ) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "Open": [
                    100.0,
                    101.0,
                    102.0,
                ],
                "High": [
                    101.0,
                    102.0,
                    103.0,
                ],
                "Low": [
                    99.0,
                    100.0,
                    101.0,
                ],
                "Close": [
                    100.5,
                    101.5,
                    102.5,
                ],
                "Volume": [
                    1000,
                    1100,
                    1200,
                ],
            },
            index=pd.date_range(
                start="2024-01-01T00:00:00Z",
                periods=3,
                freq="h",
            ),
        )


class FailingMarketSignalProvider:
    def generate(
        self,
        data: pd.DataFrame,
        specification: MarketExperimentSpecification,
    ) -> pd.DataFrame:
        raise RuntimeError(
            "signal generation failed"
        )


def build_specification(
) -> MarketExperimentSpecification:
    return MarketExperimentSpecification(
        executor_type="market_backtest",
        question_title=(
            "Is a failed production run traceable?"
        ),
        question_description=(
            "Verify persisted technical failure history."
        ),
        hypothesis_title=(
            "Execution failure remains observable"
        ),
        hypothesis_description=(
            "A failed executor should preserve its "
            "technical state transitions."
        ),
        expected_result=(
            "The failure is persisted without an artifact."
        ),
        experiment_title=(
            "Production failure lifecycle experiment"
        ),
        experiment_description=(
            "Fail during signal generation after execution starts."
        ),
        data_source="deterministic-test",
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
        entry_rule="failing signal",
        exit_rule="execution policy",
        direction=MarketPositionDirection.LONG,
        stop_loss_percent=2.0,
        take_profit_percent=2.0,
        max_holding_bars=10,
    )


def run_cli(
    database_path: Path,
    *arguments: str,
) -> object:
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


def test_market_research_failure_lifecycle_is_persisted(
    tmp_path: Path,
) -> None:
    database_path = (
        tmp_path / "research-cycles.db"
    )
    store = SqliteResearchCycleStore(
        db_path=database_path,
    )
    recorder = SqliteExperimentExecutionRecorder(
        db_path=database_path,
    )
    specification = build_specification()
    application = build_market_research_application(
        data_provider=(
            DeterministicMarketDataProvider()
        ),
        signal_provider=(
            FailingMarketSignalProvider()
        ),
        store=store,
        execution_recorder=recorder,
    )

    with pytest.raises(
        RuntimeError,
        match="signal generation failed",
    ):
        application.execute(
            specification
        )

    assert store.list_result_ids() == []

    execution_ids = (
        recorder.list_execution_ids()
    )

    assert len(execution_ids) == 1

    execution_id = execution_ids[0]
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
        "FAILED",
    ]

    pending, running, failed = history[
        "snapshots"
    ]

    assert pending[
        "specification_fingerprint"
    ] == specification.fingerprint
    assert running[
        "environment_fingerprint"
    ] is not None
    assert failed[
        "environment_fingerprint"
    ] == running[
        "environment_fingerprint"
    ]
    assert failed["result_id"] is None
    assert failed["failure"] == {
        "stage": "EXECUTION",
        "error_type": "RuntimeError",
        "message": "signal generation failed",
    }

    stored_result_ids = run_cli(
        database_path,
        "list-research-cycles",
        "--compact",
    )

    assert stored_result_ids == []

class UnavailableMarketDataProvider:
    def load(
        self,
        specification: MarketExperimentSpecification,
    ) -> pd.DataFrame:
        raise RuntimeError(
            "market data unavailable"
        )


def test_market_research_preparation_failure_is_persisted(
    tmp_path: Path,
) -> None:
    database_path = (
        tmp_path / "preparation-failure.db"
    )
    store = SqliteResearchCycleStore(
        db_path=database_path,
    )
    recorder = SqliteExperimentExecutionRecorder(
        db_path=database_path,
    )
    specification = build_specification()
    application = build_market_research_application(
        data_provider=(
            UnavailableMarketDataProvider()
        ),
        signal_provider=(
            FailingMarketSignalProvider()
        ),
        store=store,
        execution_recorder=recorder,
    )

    with pytest.raises(
        RuntimeError,
        match="market data unavailable",
    ):
        application.execute(
            specification
        )

    assert store.list_result_ids() == []

    reopened_recorder = (
        SqliteExperimentExecutionRecorder(
            db_path=database_path,
        )
    )
    execution_ids = (
        reopened_recorder.list_execution_ids()
    )

    assert len(execution_ids) == 1

    execution_id = execution_ids[0]
    history = run_cli(
        database_path,
        "get-experiment-execution-history",
        execution_id,
        "--compact",
    )

    assert history["schema_version"] == 1
    assert history["execution_id"] == execution_id
    assert history["snapshot_count"] == 2
    assert [
        snapshot["status"]
        for snapshot in history["snapshots"]
    ] == [
        "PENDING",
        "FAILED",
    ]

    pending, failed = history[
        "snapshots"
    ]

    assert pending[
        "specification_fingerprint"
    ] == specification.fingerprint
    assert failed[
        "specification_fingerprint"
    ] == specification.fingerprint
    assert failed["started_at"] is None
    assert failed[
        "environment_fingerprint"
    ] is None
    assert failed["result_id"] is None
    assert failed["finished_at"] is not None
    assert failed["failure"] == {
        "stage": "PREPARATION",
        "error_type": "RuntimeError",
        "message": "market data unavailable",
    }

    stored_result_ids = run_cli(
        database_path,
        "list-research-cycles",
        "--compact",
    )

    assert stored_result_ids == []
