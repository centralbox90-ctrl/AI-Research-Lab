from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from src.research.knowledge_item import KnowledgeItem
from src.research.knowledge_relation import (
    KnowledgeRelation,
    KnowledgeRelationType,
)
from src.research.knowledge_relation_repository import (
    KnowledgeRelationReferenceError,
)
from src.research.knowledge_repository import (
    KnowledgeRepository,
)


class SqliteKnowledgeRelationRepository:
    """
    Append-only SQLite storage for typed knowledge relations.
    """

    def __init__(
        self,
        *,
        db_path: str | Path,
        knowledge_repository: KnowledgeRepository,
    ) -> None:
        if not isinstance(
            knowledge_repository,
            KnowledgeRepository,
        ):
            raise TypeError(
                "knowledge_repository must implement "
                "KnowledgeRepository"
            )

        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        self._knowledge_repository = (
            knowledge_repository
        )
        self._create_tables()

    def save(
        self,
        relation: KnowledgeRelation,
    ) -> None:
        if not isinstance(
            relation,
            KnowledgeRelation,
        ):
            raise TypeError(
                "relation must be a "
                "KnowledgeRelation"
            )

        self._validate_endpoint(
            endpoint="source",
            item=relation.source,
        )
        self._validate_endpoint(
            endpoint="target",
            item=relation.target,
        )

        with self._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            existing = connection.execute(
                """
                SELECT payload
                FROM knowledge_relations
                WHERE fingerprint = ?
                """,
                (relation.fingerprint,),
            ).fetchone()

            if existing is not None:
                stored = self._deserialize_relation(
                    existing[0],
                    expected_fingerprint=(
                        relation.fingerprint
                    ),
                )

                if stored != relation:
                    raise ValueError(
                        "stored relation fingerprint "
                        "is bound to different content"
                    )

                return

            connection.execute(
                """
                INSERT INTO knowledge_relations (
                    fingerprint,
                    source_item_id,
                    source_version,
                    source_fingerprint,
                    target_item_id,
                    target_version,
                    target_fingerprint,
                    relation_type,
                    reason,
                    payload
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    relation.fingerprint,
                    relation.source.id,
                    relation.source.version,
                    relation.source.fingerprint,
                    relation.target.id,
                    relation.target.version,
                    relation.target.fingerprint,
                    relation.relation_type.value,
                    relation.reason,
                    self._serialize(
                        relation.to_dict()
                    ),
                ),
            )

    def list_all(
        self,
    ) -> tuple[KnowledgeRelation, ...]:
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT fingerprint, payload
                FROM knowledge_relations
                """
            ).fetchall()

        relations = tuple(
            self._deserialize_relation(
                row[1],
                expected_fingerprint=row[0],
            )
            for row in rows
        )

        return tuple(
            sorted(
                relations,
                key=self._relation_sort_key,
            )
        )

    def outgoing(
        self,
        item_id: str,
        *,
        version: int | None = None,
        relation_type: (
            KnowledgeRelationType | None
        ) = None,
    ) -> tuple[KnowledgeRelation, ...]:
        normalized_item_id = (
            self._normalize_item_id(item_id)
        )
        normalized_version = (
            self._normalize_optional_version(
                version
            )
        )
        normalized_relation_type = (
            self._normalize_optional_relation_type(
                relation_type
            )
        )

        return tuple(
            relation
            for relation in self.list_all()
            if self._matches_endpoint(
                relation.source,
                item_id=normalized_item_id,
                version=normalized_version,
            )
            and self._matches_relation_type(
                relation,
                normalized_relation_type,
            )
        )

    def incoming(
        self,
        item_id: str,
        *,
        version: int | None = None,
        relation_type: (
            KnowledgeRelationType | None
        ) = None,
    ) -> tuple[KnowledgeRelation, ...]:
        normalized_item_id = (
            self._normalize_item_id(item_id)
        )
        normalized_version = (
            self._normalize_optional_version(
                version
            )
        )
        normalized_relation_type = (
            self._normalize_optional_relation_type(
                relation_type
            )
        )

        return tuple(
            relation
            for relation in self.list_all()
            if self._matches_endpoint(
                relation.target,
                item_id=normalized_item_id,
                version=normalized_version,
            )
            and self._matches_relation_type(
                relation,
                normalized_relation_type,
            )
        )

    def relations_for(
        self,
        item_id: str,
        *,
        version: int | None = None,
        relation_type: (
            KnowledgeRelationType | None
        ) = None,
    ) -> tuple[KnowledgeRelation, ...]:
        normalized_item_id = (
            self._normalize_item_id(item_id)
        )
        normalized_version = (
            self._normalize_optional_version(
                version
            )
        )
        normalized_relation_type = (
            self._normalize_optional_relation_type(
                relation_type
            )
        )

        return tuple(
            relation
            for relation in self.list_all()
            if (
                self._matches_endpoint(
                    relation.source,
                    item_id=normalized_item_id,
                    version=normalized_version,
                )
                or self._matches_endpoint(
                    relation.target,
                    item_id=normalized_item_id,
                    version=normalized_version,
                )
            )
            and self._matches_relation_type(
                relation,
                normalized_relation_type,
            )
        )

    def _deserialize_relation(
        self,
        payload: object,
        *,
        expected_fingerprint: object,
    ) -> KnowledgeRelation:
        data = self._deserialize_object(
            payload
        )

        if data.get("schema_version") != 1:
            raise ValueError(
                "stored relation schema_version "
                "must be 1"
            )

        source = self._resolve_endpoint(
            data.get("source"),
            endpoint="source",
        )
        target = self._resolve_endpoint(
            data.get("target"),
            endpoint="target",
        )
        relation_type_value = data.get(
            "relation_type"
        )

        if not isinstance(
            relation_type_value,
            str,
        ):
            raise ValueError(
                "stored relation_type must "
                "be a string"
            )

        try:
            relation_type = KnowledgeRelationType(
                relation_type_value
            )
        except ValueError as error:
            raise ValueError(
                "stored relation_type is not supported"
            ) from error

        relation = KnowledgeRelation(
            source=source,
            target=target,
            relation_type=relation_type,
            reason=data.get("reason"),
        )

        if relation.fingerprint != expected_fingerprint:
            raise ValueError(
                "stored relation fingerprint "
                "does not match payload"
            )

        return relation

    def _resolve_endpoint(
        self,
        value: object,
        *,
        endpoint: str,
    ) -> KnowledgeItem:
        if not isinstance(value, dict):
            raise ValueError(
                f"stored {endpoint} endpoint "
                "must be an object"
            )

        item_id = value.get("id")
        version = value.get("version")
        fingerprint = value.get(
            "fingerprint"
        )

        if not isinstance(item_id, str):
            raise ValueError(
                f"stored {endpoint} ID must "
                "be a string"
            )

        if (
            not isinstance(version, int)
            or isinstance(version, bool)
        ):
            raise ValueError(
                f"stored {endpoint} version "
                "must be an integer"
            )

        if not isinstance(fingerprint, str):
            raise ValueError(
                f"stored {endpoint} fingerprint "
                "must be a string"
            )

        revision = (
            self._knowledge_repository.get_version(
                item_id,
                version,
            )
        )

        if (
            revision is None
            or revision.item.fingerprint
            != fingerprint
        ):
            raise KnowledgeRelationReferenceError(
                endpoint=endpoint,
                item_id=item_id,
                version=version,
            )

        return revision.item

    def _validate_endpoint(
        self,
        *,
        endpoint: str,
        item: KnowledgeItem,
    ) -> None:
        revision = (
            self._knowledge_repository.get_version(
                item.id,
                item.version,
            )
        )

        if (
            revision is None
            or revision.item.fingerprint
            != item.fingerprint
        ):
            raise KnowledgeRelationReferenceError(
                endpoint=endpoint,
                item_id=item.id,
                version=item.version,
            )

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
    ) -> dict[str, Any]:
        if not isinstance(value, str):
            raise ValueError(
                "stored relation payload "
                "must be a string"
            )

        try:
            data = json.loads(value)
        except json.JSONDecodeError as error:
            raise ValueError(
                "stored relation payload "
                "must be valid JSON"
            ) from error

        if not isinstance(data, dict):
            raise ValueError(
                "stored relation payload "
                "must be an object"
            )

        return data

    @staticmethod
    def _relation_sort_key(
        relation: KnowledgeRelation,
    ) -> tuple[object, ...]:
        return (
            relation.source.id,
            relation.source.version,
            relation.source.fingerprint,
            relation.relation_type.value,
            relation.target.id,
            relation.target.version,
            relation.target.fingerprint,
            relation.reason,
            relation.fingerprint,
        )

    @staticmethod
    def _matches_endpoint(
        item: KnowledgeItem,
        *,
        item_id: str,
        version: int | None,
    ) -> bool:
        return (
            item.id == item_id
            and (
                version is None
                or item.version == version
            )
        )

    @staticmethod
    def _matches_relation_type(
        relation: KnowledgeRelation,
        relation_type: (
            KnowledgeRelationType | None
        ),
    ) -> bool:
        return (
            relation_type is None
            or relation.relation_type
            is relation_type
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
    def _normalize_optional_version(
        value: object,
    ) -> int | None:
        if value is None:
            return None

        if (
            not isinstance(value, int)
            or isinstance(value, bool)
        ):
            raise TypeError(
                "version must be an integer "
                "or None"
            )

        if value < 1:
            raise ValueError(
                "version must be positive"
            )

        return value

    @staticmethod
    def _normalize_optional_relation_type(
        value: object,
    ) -> KnowledgeRelationType | None:
        if value is None:
            return None

        if not isinstance(
            value,
            KnowledgeRelationType,
        ):
            raise TypeError(
                "relation_type must be a "
                "KnowledgeRelationType or None"
            )

        return value

    def _get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(
            self.db_path
        )

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
                CREATE TABLE IF NOT EXISTS
                knowledge_relations (
                    fingerprint TEXT PRIMARY KEY,
                    source_item_id TEXT NOT NULL,
                    source_version INTEGER NOT NULL
                        CHECK (source_version > 0),
                    source_fingerprint TEXT NOT NULL,
                    target_item_id TEXT NOT NULL,
                    target_version INTEGER NOT NULL
                        CHECK (target_version > 0),
                    target_fingerprint TEXT NOT NULL,
                    relation_type TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    payload TEXT NOT NULL
                )
                """
            )
