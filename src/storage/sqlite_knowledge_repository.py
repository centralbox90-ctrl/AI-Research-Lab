from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any

from src.research.knowledge_applicability_query import (
    KnowledgeApplicabilityQuery,
)
from src.research.knowledge_contradiction import (
    KnowledgeContradiction,
)
from src.research.knowledge_item import KnowledgeItem
from src.research.knowledge_repository import (
    KnowledgeItemConflictError,
    KnowledgeRevisionSequenceError,
)
from src.research.knowledge_revision import (
    KnowledgeRevision,
)


class SqliteKnowledgeRepository:
    """
    Append-only SQLite storage for knowledge history and contradictions.
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
        revision: KnowledgeRevision,
    ) -> None:
        if not isinstance(
            revision,
            KnowledgeRevision,
        ):
            raise TypeError(
                "revision must be a KnowledgeRevision"
            )

        item_id = revision.item.id
        version = revision.item.version

        with self._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            existing = connection.execute(
                """
                SELECT revision_fingerprint
                FROM knowledge_revisions
                WHERE item_id = ? AND version = ?
                """,
                (
                    item_id,
                    version,
                ),
            ).fetchone()

            if existing is not None:
                existing_fingerprint = str(
                    existing[0]
                )

                if (
                    existing_fingerprint
                    != revision.fingerprint
                ):
                    raise KnowledgeItemConflictError(
                        item_id=item_id,
                        version=version,
                        existing_fingerprint=(
                            existing_fingerprint
                        ),
                        incoming_fingerprint=(
                            revision.fingerprint
                        ),
                    )

                return

            latest = connection.execute(
                """
                SELECT version, valid_from
                FROM knowledge_revisions
                WHERE item_id = ?
                ORDER BY version DESC
                LIMIT 1
                """,
                (item_id,),
            ).fetchone()

            if latest is None:
                expected_version = 1
            else:
                expected_version = int(
                    latest[0]
                ) + 1

            if version != expected_version:
                raise KnowledgeRevisionSequenceError(
                    item_id=item_id,
                    expected_version=expected_version,
                    incoming_version=version,
                )

            if latest is not None:
                latest_valid_from = (
                    self._parse_datetime(
                        latest[1],
                        context=(
                            "stored revision valid_from"
                        ),
                    )
                )

                if (
                    revision.valid_from
                    <= latest_valid_from
                ):
                    raise ValueError(
                        "revision valid_from must be later "
                        "than the latest stored revision"
                    )

            connection.execute(
                """
                INSERT INTO knowledge_revisions (
                    item_id,
                    version,
                    item_fingerprint,
                    revision_fingerprint,
                    valid_from,
                    payload
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    item_id,
                    version,
                    revision.item.fingerprint,
                    revision.fingerprint,
                    self._format_datetime(
                        revision.valid_from
                    ),
                    self._serialize(
                        revision.to_dict()
                    ),
                ),
            )

    def get(
        self,
        item_id: str,
    ) -> KnowledgeItem | None:
        normalized_item_id = (
            self._normalize_item_id(item_id)
        )

        with self._connection() as connection:
            row = connection.execute(
                """
                SELECT payload, revision_fingerprint
                FROM knowledge_revisions
                WHERE item_id = ?
                ORDER BY version DESC
                LIMIT 1
                """,
                (normalized_item_id,),
            ).fetchone()

        if row is None:
            return None

        return self._deserialize_revision(
            row[0],
            expected_fingerprint=row[1],
        ).item

    def get_version(
        self,
        item_id: str,
        version: int,
    ) -> KnowledgeRevision | None:
        normalized_item_id = (
            self._normalize_item_id(item_id)
        )
        normalized_version = (
            self._normalize_version(version)
        )

        with self._connection() as connection:
            row = connection.execute(
                """
                SELECT payload, revision_fingerprint
                FROM knowledge_revisions
                WHERE item_id = ? AND version = ?
                """,
                (
                    normalized_item_id,
                    normalized_version,
                ),
            ).fetchone()

        if row is None:
            return None

        return self._deserialize_revision(
            row[0],
            expected_fingerprint=row[1],
        )

    def history(
        self,
        item_id: str,
    ) -> tuple[KnowledgeRevision, ...]:
        normalized_item_id = (
            self._normalize_item_id(item_id)
        )

        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT payload, revision_fingerprint
                FROM knowledge_revisions
                WHERE item_id = ?
                ORDER BY version
                """,
                (normalized_item_id,),
            ).fetchall()

        return tuple(
            self._deserialize_revision(
                row[0],
                expected_fingerprint=row[1],
            )
            for row in rows
        )

    def list_all(
        self,
    ) -> tuple[KnowledgeItem, ...]:
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT
                    revision.payload,
                    revision.revision_fingerprint
                FROM knowledge_revisions AS revision
                INNER JOIN (
                    SELECT item_id, MAX(version) AS version
                    FROM knowledge_revisions
                    GROUP BY item_id
                ) AS latest
                    ON latest.item_id = revision.item_id
                    AND latest.version = revision.version
                ORDER BY revision.item_id
                """
            ).fetchall()

        return tuple(
            self._deserialize_revision(
                row[0],
                expected_fingerprint=row[1],
            ).item
            for row in rows
        )

    def find_applicable(
        self,
        query: KnowledgeApplicabilityQuery,
    ) -> tuple[KnowledgeItem, ...]:
        if not isinstance(
            query,
            KnowledgeApplicabilityQuery,
        ):
            raise TypeError(
                "query must be a "
                "KnowledgeApplicabilityQuery"
            )

        return tuple(
            item
            for item in self.list_all()
            if query.matches(item)
        )

    def save_contradiction(
        self,
        contradiction: KnowledgeContradiction,
    ) -> None:
        if not isinstance(
            contradiction,
            KnowledgeContradiction,
        ):
            raise TypeError(
                "contradiction must be a "
                "KnowledgeContradiction"
            )

        with self._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")

            for item in contradiction.items:
                row = connection.execute(
                    """
                    SELECT item_fingerprint
                    FROM knowledge_revisions
                    WHERE item_id = ? AND version = ?
                    """,
                    (
                        item.id,
                        item.version,
                    ),
                ).fetchone()

                if (
                    row is None
                    or str(row[0])
                    != item.fingerprint
                ):
                    raise ValueError(
                        "contradiction items must "
                        "reference stored knowledge versions"
                    )

            left, right = contradiction.items
            connection.execute(
                """
                INSERT OR IGNORE
                INTO knowledge_contradictions (
                    fingerprint,
                    left_item_id,
                    left_version,
                    right_item_id,
                    right_version,
                    payload
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    contradiction.fingerprint,
                    left.id,
                    left.version,
                    right.id,
                    right.version,
                    self._serialize(
                        contradiction.to_dict()
                    ),
                ),
            )

    def list_contradictions(
        self,
    ) -> tuple[KnowledgeContradiction, ...]:
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT fingerprint, payload
                FROM knowledge_contradictions
                """
            ).fetchall()
            contradictions = tuple(
                self._deserialize_contradiction(
                    connection,
                    row[1],
                    expected_fingerprint=row[0],
                )
                for row in rows
            )

        return tuple(
            sorted(
                contradictions,
                key=self._contradiction_sort_key,
            )
        )

    def contradictions_for(
        self,
        item_id: str,
    ) -> tuple[KnowledgeContradiction, ...]:
        normalized_item_id = (
            self._normalize_item_id(item_id)
        )

        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT fingerprint, payload
                FROM knowledge_contradictions
                WHERE
                    left_item_id = ?
                    OR right_item_id = ?
                """,
                (
                    normalized_item_id,
                    normalized_item_id,
                ),
            ).fetchall()
            contradictions = tuple(
                self._deserialize_contradiction(
                    connection,
                    row[1],
                    expected_fingerprint=row[0],
                )
                for row in rows
            )

        return tuple(
            sorted(
                contradictions,
                key=self._contradiction_sort_key,
            )
        )

    def _deserialize_contradiction(
        self,
        connection: sqlite3.Connection,
        payload: object,
        *,
        expected_fingerprint: object,
    ) -> KnowledgeContradiction:
        data = self._deserialize_object(
            payload,
            context="stored contradiction",
        )

        if data.get("schema_version") != 1:
            raise ValueError(
                "stored contradiction schema_version "
                "must be 1"
            )

        references = data.get("items")

        if (
            not isinstance(references, list)
            or len(references) != 2
        ):
            raise ValueError(
                "stored contradiction items must "
                "contain two references"
            )

        items: list[KnowledgeItem] = []

        for reference in references:
            if not isinstance(reference, dict):
                raise ValueError(
                    "stored contradiction item "
                    "reference must be an object"
                )

            item_id = reference.get("id")
            version = reference.get("version")
            fingerprint = reference.get(
                "fingerprint"
            )
            row = connection.execute(
                """
                SELECT payload, revision_fingerprint
                FROM knowledge_revisions
                WHERE item_id = ? AND version = ?
                """,
                (
                    item_id,
                    version,
                ),
            ).fetchone()

            if row is None:
                raise ValueError(
                    "stored contradiction references "
                    "a missing knowledge version"
                )

            item = self._deserialize_revision(
                row[0],
                expected_fingerprint=row[1],
            ).item

            if item.fingerprint != fingerprint:
                raise ValueError(
                    "stored contradiction item "
                    "fingerprint does not match"
                )

            items.append(item)

        contradiction = KnowledgeContradiction(
            items=(
                items[0],
                items[1],
            ),
            reason=data.get("reason"),
        )

        if (
            contradiction.fingerprint
            != expected_fingerprint
        ):
            raise ValueError(
                "stored contradiction fingerprint "
                "does not match payload"
            )

        if list(
            contradiction.conflicting_applicability
        ) != data.get(
            "conflicting_applicability"
        ):
            raise ValueError(
                "stored contradiction applicability "
                "does not match items"
            )

        return contradiction

    @classmethod
    def _deserialize_revision(
        cls,
        payload: object,
        *,
        expected_fingerprint: object,
    ) -> KnowledgeRevision:
        data = cls._deserialize_object(
            payload,
            context="stored revision",
        )

        if data.get("schema_version") != 1:
            raise ValueError(
                "stored revision schema_version "
                "must be 1"
            )

        item_data = data.get("item")

        if not isinstance(item_data, dict):
            raise ValueError(
                "stored revision item must be an object"
            )

        if item_data.get("schema_version") != 1:
            raise ValueError(
                "stored knowledge item schema_version "
                "must be 1"
            )

        provenance = item_data.get(
            "provenance"
        )

        if not isinstance(provenance, dict):
            raise ValueError(
                "stored knowledge item provenance "
                "must be an object"
            )

        item = KnowledgeItem(
            id=item_data.get("id"),
            statement=item_data.get("statement"),
            confidence=item_data.get(
                "confidence"
            ),
            applicability=cls._as_tuple(
                item_data.get("applicability"),
                context=(
                    "stored knowledge item applicability"
                ),
            ),
            limitations=cls._as_tuple(
                item_data.get("limitations"),
                context=(
                    "stored knowledge item limitations"
                ),
            ),
            supporting_findings=cls._as_tuple(
                item_data.get(
                    "supporting_findings"
                ),
                context=(
                    "stored knowledge item "
                    "supporting_findings"
                ),
            ),
            version=item_data.get("version"),
            provenance=tuple(
                provenance.items()
            ),
        )

        if (
            item.fingerprint
            != data.get("item_fingerprint")
        ):
            raise ValueError(
                "stored knowledge item fingerprint "
                "does not match payload"
            )

        revision = KnowledgeRevision(
            item=item,
            valid_from=cls._parse_datetime(
                data.get("valid_from"),
                context=(
                    "stored revision valid_from"
                ),
            ),
            change_reason=data.get(
                "change_reason"
            ),
            supersedes_version=data.get(
                "supersedes_version"
            ),
        )

        if revision.fingerprint != expected_fingerprint:
            raise ValueError(
                "stored revision fingerprint "
                "does not match payload"
            )

        return revision

    @staticmethod
    def _serialize(
        value: dict[str, object],
    ) -> str:
        return json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )

    @staticmethod
    def _deserialize_object(
        value: object,
        *,
        context: str,
    ) -> dict[str, Any]:
        if not isinstance(value, str):
            raise ValueError(
                f"{context} payload must be a string"
            )

        try:
            data = json.loads(value)
        except json.JSONDecodeError as error:
            raise ValueError(
                f"{context} payload must be valid JSON"
            ) from error

        if not isinstance(data, dict):
            raise ValueError(
                f"{context} payload must be an object"
            )

        return data

    @staticmethod
    def _as_tuple(
        value: object,
        *,
        context: str,
    ) -> tuple[Any, ...]:
        if not isinstance(value, list):
            raise ValueError(
                f"{context} must be an array"
            )

        return tuple(value)

    @staticmethod
    def _format_datetime(
        value: datetime,
    ) -> str:
        return (
            value.isoformat()
            .replace("+00:00", "Z")
        )

    @staticmethod
    def _parse_datetime(
        value: object,
        *,
        context: str,
    ) -> datetime:
        if not isinstance(value, str):
            raise ValueError(
                f"{context} must be a string"
            )

        normalized = (
            value[:-1] + "+00:00"
            if value.endswith("Z")
            else value
        )

        try:
            return datetime.fromisoformat(
                normalized
            )
        except ValueError as error:
            raise ValueError(
                f"{context} must be ISO-8601"
            ) from error

    @staticmethod
    def _contradiction_sort_key(
        contradiction: KnowledgeContradiction,
    ) -> tuple[object, ...]:
        return (
            tuple(
                (
                    item.id,
                    item.version,
                    item.fingerprint,
                )
                for item in contradiction.items
            ),
            contradiction.reason,
            contradiction.fingerprint,
        )

    @staticmethod
    def _normalize_item_id(
        value: object,
    ) -> str:
        if not isinstance(value, str):
            raise TypeError(
                "item_id must be a string"
            )

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                "item_id must not be empty"
            )

        return normalized

    @staticmethod
    def _normalize_version(
        value: object,
    ) -> int:
        if (
            not isinstance(value, int)
            or isinstance(value, bool)
        ):
            raise TypeError(
                "version must be an integer"
            )

        if value < 1:
            raise ValueError(
                "version must be positive"
            )

        return value

    def _get_connection(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            self.db_path
        )
        connection.execute(
            "PRAGMA foreign_keys = ON"
        )

        return connection

    @contextmanager
    def _connection(
        self,
    ) -> Iterator[sqlite3.Connection]:
        connection = self._get_connection()

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
                CREATE TABLE IF NOT EXISTS knowledge_revisions (
                    item_id TEXT NOT NULL,
                    version INTEGER NOT NULL
                        CHECK (version > 0),
                    item_fingerprint TEXT NOT NULL,
                    revision_fingerprint TEXT NOT NULL,
                    valid_from TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    PRIMARY KEY (item_id, version)
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS
                knowledge_contradictions (
                    fingerprint TEXT PRIMARY KEY,
                    left_item_id TEXT NOT NULL,
                    left_version INTEGER NOT NULL,
                    right_item_id TEXT NOT NULL,
                    right_version INTEGER NOT NULL,
                    payload TEXT NOT NULL,
                    FOREIGN KEY (
                        left_item_id,
                        left_version
                    )
                    REFERENCES knowledge_revisions (
                        item_id,
                        version
                    ),
                    FOREIGN KEY (
                        right_item_id,
                        right_version
                    )
                    REFERENCES knowledge_revisions (
                        item_id,
                        version
                    )
                )
                """
            )
