from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any

from src.research.experiment_execution import (
    ExperimentExecution,
    ExperimentExecutionFailure,
    ExperimentExecutionFailureStage,
    ExperimentExecutionStatus,
)


class SqliteExperimentExecutionRecorder:
    """
    Append-only SQLite storage for ExperimentExecution snapshots.

    Each record call adds the supplied immutable state as the next
    snapshot of the same execution.
    """

    def __init__(
        self,
        db_path: str | Path,
    ) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        self._create_tables()

    def record(
        self,
        execution: ExperimentExecution,
    ) -> None:
        if not isinstance(
            execution,
            ExperimentExecution,
        ):
            raise TypeError(
                "execution must be an ExperimentExecution"
            )

        payload = json.dumps(
            execution.to_dict(),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )

        with self._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")

            row = connection.execute(
                """
                SELECT COALESCE(MAX(sequence), 0)
                FROM experiment_execution_snapshots
                WHERE execution_id = ?
                """,
                (execution.execution_id,),
            ).fetchone()

            sequence = int(row[0]) + 1

            connection.execute(
                """
                INSERT INTO experiment_execution_snapshots (
                    execution_id,
                    sequence,
                    status,
                    payload
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    execution.execution_id,
                    sequence,
                    execution.status.value,
                    payload,
                ),
            )

    def get_latest(
        self,
        execution_id: str,
    ) -> ExperimentExecution | None:
        normalized_id = _normalize_execution_id(
            execution_id
        )

        with self._connection() as connection:
            row = connection.execute(
                """
                SELECT payload
                FROM experiment_execution_snapshots
                WHERE execution_id = ?
                ORDER BY sequence DESC
                LIMIT 1
                """,
                (normalized_id,),
            ).fetchone()

        if row is None:
            return None

        return _deserialize_execution(row[0])

    def history(
        self,
        execution_id: str,
    ) -> tuple[ExperimentExecution, ...]:
        normalized_id = _normalize_execution_id(
            execution_id
        )

        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT payload
                FROM experiment_execution_snapshots
                WHERE execution_id = ?
                ORDER BY sequence
                """,
                (normalized_id,),
            ).fetchall()

        return tuple(
            _deserialize_execution(row[0])
            for row in rows
        )

    def list_execution_ids(
        self,
    ) -> tuple[str, ...]:
        """Return distinct execution identities deterministically."""

        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT DISTINCT execution_id
                FROM experiment_execution_snapshots
                ORDER BY execution_id
                """
            ).fetchall()

        return tuple(
            str(row[0])
            for row in rows
        )

    @contextmanager
    def _connection(
        self,
    ) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.db_path)

        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _create_tables(self) -> None:
        with self._connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS
                experiment_execution_snapshots (
                    execution_id TEXT NOT NULL,
                    sequence INTEGER NOT NULL
                        CHECK (sequence > 0),
                    status TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    PRIMARY KEY (
                        execution_id,
                        sequence
                    )
                )
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_experiment_execution_status
                ON experiment_execution_snapshots (
                    status,
                    execution_id,
                    sequence
                )
                """
            )


def _deserialize_execution(
    payload: object,
) -> ExperimentExecution:
    if not isinstance(payload, str):
        raise TypeError(
            "Stored execution payload must be a string"
        )

    try:
        data = json.loads(payload)
    except json.JSONDecodeError as error:
        raise ValueError(
            "Stored execution payload is not valid JSON"
        ) from error

    if not isinstance(data, dict):
        raise TypeError(
            "Stored execution payload must be an object"
        )

    if data.get("schema_version") != 1:
        raise ValueError(
            "Stored execution schema version is not supported"
        )

    required_fields = (
        "execution_id",
        "experiment_id",
        "specification_fingerprint",
        "correlation_id",
        "environment_fingerprint",
        "status",
        "created_at",
        "started_at",
        "finished_at",
        "result_id",
        "failure",
    )

    for field_name in required_fields:
        if field_name not in data:
            raise ValueError(
                "Stored execution payload is missing "
                f"{field_name}"
            )

    return ExperimentExecution(
        execution_id=data["execution_id"],
        experiment_id=data["experiment_id"],
        specification_fingerprint=(
            data["specification_fingerprint"]
        ),
        correlation_id=data["correlation_id"],
        environment_fingerprint=(
            data["environment_fingerprint"]
        ),
        status=_deserialize_status(
            data["status"]
        ),
        created_at=_deserialize_timestamp(
            data["created_at"],
            field_name="created_at",
        ),
        started_at=_deserialize_optional_timestamp(
            data["started_at"],
            field_name="started_at",
        ),
        finished_at=_deserialize_optional_timestamp(
            data["finished_at"],
            field_name="finished_at",
        ),
        result_id=data["result_id"],
        failure=_deserialize_failure(
            data["failure"]
        ),
    )


def _deserialize_status(
    value: object,
) -> ExperimentExecutionStatus:
    if not isinstance(value, str):
        raise TypeError(
            "Stored execution status must be a string"
        )

    try:
        return ExperimentExecutionStatus(value)
    except ValueError as error:
        raise ValueError(
            "Stored execution status is not supported"
        ) from error


def _deserialize_failure(
    value: object,
) -> ExperimentExecutionFailure | None:
    if value is None:
        return None

    if not isinstance(value, dict):
        raise TypeError(
            "Stored execution failure must be an object"
        )

    required_fields = (
        "stage",
        "error_type",
        "message",
    )

    for field_name in required_fields:
        if field_name not in value:
            raise ValueError(
                "Stored execution failure is missing "
                f"{field_name}"
            )

    stage_value = value["stage"]

    if not isinstance(stage_value, str):
        raise TypeError(
            "Stored execution failure stage "
            "must be a string"
        )

    try:
        stage = ExperimentExecutionFailureStage(
            stage_value
        )
    except ValueError as error:
        raise ValueError(
            "Stored execution failure stage "
            "is not supported"
        ) from error

    return ExperimentExecutionFailure(
        stage=stage,
        error_type=value["error_type"],
        message=value["message"],
    )


def _deserialize_timestamp(
    value: object,
    *,
    field_name: str,
) -> datetime:
    if not isinstance(value, str):
        raise TypeError(
            f"Stored {field_name} must be a string"
        )

    try:
        return datetime.fromisoformat(value)
    except ValueError as error:
        raise ValueError(
            f"Stored {field_name} is not a valid timestamp"
        ) from error


def _deserialize_optional_timestamp(
    value: object,
    *,
    field_name: str,
) -> datetime | None:
    if value is None:
        return None

    return _deserialize_timestamp(
        value,
        field_name=field_name,
    )


def _normalize_execution_id(
    value: object,
) -> str:
    if not isinstance(value, str):
        raise TypeError(
            "execution_id must be a string"
        )

    normalized = value.strip()

    if not normalized:
        raise ValueError(
            "execution_id must not be empty"
        )

    return normalized
