import json
import sqlite3
from pathlib import Path
from typing import Any


class SqliteResearchCycleStore:
    """
    SQLite storage adapter for serialized research cycles.

    The store accepts only application-safe dictionaries. It does not
    import research domain models and does not reconstruct domain cycles.
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

    def save(
        self,
        result_id: str,
        serialized_cycle: dict[str, Any],
    ) -> None:
        payload = json.dumps(
            serialized_cycle,
            ensure_ascii=False,
            sort_keys=True,
        )

        with self._get_connection() as connection:
            connection.execute("BEGIN IMMEDIATE")

            row = connection.execute(
                """
                SELECT payload
                FROM research_cycles
                WHERE result_id = ?
                """,
                (result_id,),
            ).fetchone()

            if row is None:
                connection.execute(
                    """
                    INSERT INTO research_cycles (
                        result_id,
                        payload
                    )
                    VALUES (?, ?)
                    """,
                    (
                        result_id,
                        payload,
                    ),
                )
                return

            if str(row[0]) != payload:
                raise ValueError(
                    "result_id already stores a "
                    "different research cycle"
                )

    def get(
        self,
        result_id: str,
    ) -> dict[str, Any] | None:
        with self._get_connection() as connection:
            row = connection.execute(
                """
                SELECT payload
                FROM research_cycles
                WHERE result_id = ?
                """,
                (result_id,),
            ).fetchone()

        if row is None:
            return None

        payload = json.loads(row[0])

        if not isinstance(payload, dict):
            raise TypeError(
                "Stored research cycle payload must be a dictionary."
            )

        return payload

    def list_result_ids(self) -> list[str]:
        with self._get_connection() as connection:
            rows = connection.execute(
                """
                SELECT result_id
                FROM research_cycles
                ORDER BY result_id
                """
            ).fetchall()

        return [
            str(row[0])
            for row in rows
        ]

    def is_ready(self) -> bool:
        try:
            with self._get_connection() as connection:
                connection.execute("SELECT 1").fetchone()
        except sqlite3.Error:
            return False

        return True

    def _get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _create_tables(self) -> None:
        with self._get_connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS research_cycles (
                    result_id TEXT PRIMARY KEY,
                    payload TEXT NOT NULL
                )
                """
            )