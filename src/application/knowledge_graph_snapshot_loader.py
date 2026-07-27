from __future__ import annotations

import json
from json import JSONDecodeError
from pathlib import Path
from typing import Any

from src.research.knowledge_graph_snapshot import (
    KnowledgeGraphSnapshot,
)
from src.research.knowledge_item import KnowledgeItem
from src.research.knowledge_relation import (
    KnowledgeRelation,
    KnowledgeRelationType,
)


class KnowledgeGraphSnapshotLoader:
    """
    Loads a strict schema-v1 KnowledgeGraphSnapshot from JSON.
    """

    SCHEMA_VERSION = 1

    _SNAPSHOT_FIELDS = {
        "schema_version",
        "items",
        "relations",
    }
    _ITEM_FIELDS = {
        "schema_version",
        "id",
        "statement",
        "confidence",
        "applicability",
        "limitations",
        "supporting_findings",
        "version",
        "provenance",
        "fingerprint",
    }
    _RELATION_FIELDS = {
        "schema_version",
        "source",
        "target",
        "relation_type",
        "reason",
    }
    _ENDPOINT_FIELDS = {
        "id",
        "version",
        "fingerprint",
    }

    def load(
        self,
        path: str | Path,
    ) -> KnowledgeGraphSnapshot:
        snapshot_path = Path(path)

        try:
            source = snapshot_path.read_text(
                encoding="utf-8",
            )
        except OSError as error:
            raise ValueError(
                "unable to read knowledge graph "
                f"snapshot file: {snapshot_path}"
            ) from error

        try:
            payload = json.loads(source)
        except JSONDecodeError as error:
            raise ValueError(
                "invalid knowledge graph snapshot "
                f"JSON: {error.msg}"
            ) from error

        return self.from_dict(payload)

    def from_dict(
        self,
        payload: Any,
    ) -> KnowledgeGraphSnapshot:
        snapshot_payload = self._require_object(
            payload,
            context="snapshot",
        )
        self._validate_fields(
            snapshot_payload,
            expected=self._SNAPSHOT_FIELDS,
            context="snapshot",
        )
        self._validate_schema_version(
            snapshot_payload,
            context="snapshot",
        )

        item_payloads = snapshot_payload["items"]
        relation_payloads = snapshot_payload[
            "relations"
        ]

        if not isinstance(item_payloads, list):
            raise ValueError(
                "snapshot.items must be an array"
            )

        if not isinstance(
            relation_payloads,
            list,
        ):
            raise ValueError(
                "snapshot.relations must be an array"
            )

        items = tuple(
            self._parse_item(
                item_payload,
                index=index,
            )
            for index, item_payload
            in enumerate(item_payloads)
        )
        items_by_reference = {
            self._item_reference(item): item
            for item in items
        }
        relations = tuple(
            self._parse_relation(
                relation_payload,
                index=index,
                items_by_reference=(
                    items_by_reference
                ),
            )
            for index, relation_payload
            in enumerate(relation_payloads)
        )

        return KnowledgeGraphSnapshot(
            items=items,
            relations=relations,
        )

    def _parse_item(
        self,
        payload: Any,
        *,
        index: int,
    ) -> KnowledgeItem:
        context = f"snapshot.items[{index}]"
        item_payload = self._require_object(
            payload,
            context=context,
        )
        self._validate_fields(
            item_payload,
            expected=self._ITEM_FIELDS,
            context=context,
        )
        self._validate_schema_version(
            item_payload,
            context=context,
        )

        applicability = self._require_array(
            item_payload["applicability"],
            context=f"{context}.applicability",
        )
        limitations = self._require_array(
            item_payload["limitations"],
            context=f"{context}.limitations",
        )
        supporting_findings = (
            self._require_array(
                item_payload[
                    "supporting_findings"
                ],
                context=(
                    f"{context}."
                    "supporting_findings"
                ),
            )
        )
        provenance = self._require_object(
            item_payload["provenance"],
            context=f"{context}.provenance",
        )
        item = KnowledgeItem(
            id=item_payload["id"],
            statement=item_payload["statement"],
            confidence=item_payload["confidence"],
            applicability=tuple(applicability),
            limitations=tuple(limitations),
            supporting_findings=tuple(
                supporting_findings
            ),
            version=item_payload["version"],
            provenance=tuple(
                provenance.items()
            ),
        )
        supplied_fingerprint = item_payload[
            "fingerprint"
        ]

        if not isinstance(
            supplied_fingerprint,
            str,
        ):
            raise ValueError(
                f"{context}.fingerprint must be "
                "a string"
            )

        if supplied_fingerprint != item.fingerprint:
            raise ValueError(
                f"{context}.fingerprint must "
                "match the computed item "
                "fingerprint"
            )

        return item

    def _parse_relation(
        self,
        payload: Any,
        *,
        index: int,
        items_by_reference: dict[
            tuple[str, int, str],
            KnowledgeItem,
        ],
    ) -> KnowledgeRelation:
        context = (
            f"snapshot.relations[{index}]"
        )
        relation_payload = self._require_object(
            payload,
            context=context,
        )
        self._validate_fields(
            relation_payload,
            expected=self._RELATION_FIELDS,
            context=context,
        )
        self._validate_schema_version(
            relation_payload,
            context=context,
        )
        source = self._resolve_endpoint(
            relation_payload["source"],
            context=f"{context}.source",
            items_by_reference=(
                items_by_reference
            ),
        )
        target = self._resolve_endpoint(
            relation_payload["target"],
            context=f"{context}.target",
            items_by_reference=(
                items_by_reference
            ),
        )
        relation_type_value = relation_payload[
            "relation_type"
        ]

        if not isinstance(
            relation_type_value,
            str,
        ):
            raise ValueError(
                f"{context}.relation_type must "
                "be a string"
            )

        try:
            relation_type = KnowledgeRelationType(
                relation_type_value
            )
        except ValueError as error:
            raise ValueError(
                f"{context}.relation_type is "
                "not supported"
            ) from error

        return KnowledgeRelation(
            source=source,
            target=target,
            relation_type=relation_type,
            reason=relation_payload["reason"],
        )

    def _resolve_endpoint(
        self,
        payload: Any,
        *,
        context: str,
        items_by_reference: dict[
            tuple[str, int, str],
            KnowledgeItem,
        ],
    ) -> KnowledgeItem:
        endpoint = self._require_object(
            payload,
            context=context,
        )
        self._validate_fields(
            endpoint,
            expected=self._ENDPOINT_FIELDS,
            context=context,
        )
        item_id = endpoint["id"]
        version = endpoint["version"]
        fingerprint = endpoint[
            "fingerprint"
        ]

        if not isinstance(item_id, str):
            raise ValueError(
                f"{context}.id must be a string"
            )

        if (
            not isinstance(version, int)
            or isinstance(version, bool)
        ):
            raise ValueError(
                f"{context}.version must be "
                "an integer"
            )

        if not isinstance(fingerprint, str):
            raise ValueError(
                f"{context}.fingerprint must be "
                "a string"
            )

        reference = (
            item_id,
            version,
            fingerprint,
        )

        try:
            return items_by_reference[reference]
        except KeyError as error:
            raise ValueError(
                f"{context} must reference an "
                "exact snapshot item"
            ) from error

    def _validate_schema_version(
        self,
        payload: dict[Any, Any],
        *,
        context: str,
    ) -> None:
        schema_version = payload[
            "schema_version"
        ]

        if (
            not isinstance(schema_version, int)
            or isinstance(schema_version, bool)
            or schema_version
            != self.SCHEMA_VERSION
        ):
            raise ValueError(
                f"{context}.schema_version "
                "must be 1"
            )

    @staticmethod
    def _require_object(
        value: Any,
        *,
        context: str,
    ) -> dict[Any, Any]:
        if not isinstance(value, dict):
            raise ValueError(
                f"{context} must be an object"
            )

        return value

    @staticmethod
    def _require_array(
        value: Any,
        *,
        context: str,
    ) -> list[Any]:
        if not isinstance(value, list):
            raise ValueError(
                f"{context} must be an array"
            )

        return value

    @staticmethod
    def _validate_fields(
        payload: dict[Any, Any],
        *,
        expected: set[str],
        context: str,
    ) -> None:
        if any(
            not isinstance(key, str)
            for key in payload
        ):
            raise ValueError(
                f"{context} field names must "
                "be strings"
            )

        fields = set(payload)
        missing_fields = sorted(
            expected - fields
        )

        if missing_fields:
            raise ValueError(
                f"missing {context} fields: "
                + ", ".join(missing_fields)
            )

        unknown_fields = sorted(
            fields - expected
        )

        if unknown_fields:
            raise ValueError(
                f"unknown {context} fields: "
                + ", ".join(unknown_fields)
            )

    @staticmethod
    def _item_reference(
        item: KnowledgeItem,
    ) -> tuple[str, int, str]:
        return (
            item.id,
            item.version,
            item.fingerprint,
        )
