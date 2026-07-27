import json
from copy import deepcopy
from pathlib import Path

import pytest

from src.application.knowledge_graph_snapshot_loader import (
    KnowledgeGraphSnapshotLoader,
)
from src.research.knowledge_graph_snapshot import (
    KnowledgeGraphSnapshot,
)
from src.research.knowledge_item import KnowledgeItem
from src.research.knowledge_relation import (
    KnowledgeRelation,
    KnowledgeRelationType,
)


def build_item(
    item_id: str,
    *,
    version: int = 1,
) -> KnowledgeItem:
    return KnowledgeItem(
        id=item_id,
        statement=f"Statement {item_id}.",
        confidence=0.85,
        applicability=(
            "liquid markets",
        ),
        limitations=(
            "limited history",
        ),
        supporting_findings=(
            f"{item_id}-finding-a",
        ),
        version=version,
        provenance=(
            (
                "source",
                f"{item_id}-source",
            ),
        ),
    )


def build_snapshot(
) -> KnowledgeGraphSnapshot:
    source = build_item("knowledge-a")
    target = build_item("knowledge-b")
    relation = KnowledgeRelation(
        source=source,
        target=target,
        relation_type=(
            KnowledgeRelationType.SUPPORTS
        ),
        reason="Independent evidence.",
    )

    return KnowledgeGraphSnapshot(
        items=(target, source),
        relations=(relation,),
    )


def build_payload() -> dict[str, object]:
    return build_snapshot().to_dict()


def test_round_trips_snapshot_dict(
) -> None:
    expected = build_snapshot()

    actual = (
        KnowledgeGraphSnapshotLoader()
        .from_dict(expected.to_dict())
    )

    assert actual == expected
    assert actual.to_dict() == (
        expected.to_dict()
    )
    assert actual.to_json() == (
        expected.to_json()
    )
    assert actual.fingerprint == (
        expected.fingerprint
    )


def test_loads_utf8_json_file(
    tmp_path: Path,
) -> None:
    expected = build_snapshot()
    path = tmp_path / "snapshot.json"
    path.write_text(
        expected.to_json(),
        encoding="utf-8",
    )

    actual = (
        KnowledgeGraphSnapshotLoader()
        .load(path)
    )

    assert actual == expected


def test_canonicalizes_external_order(
) -> None:
    payload = build_payload()
    payload["items"] = list(
        reversed(payload["items"])
    )

    actual = (
        KnowledgeGraphSnapshotLoader()
        .from_dict(payload)
    )

    assert actual == build_snapshot()


@pytest.mark.parametrize(
    "payload",
    (
        None,
        [],
        "snapshot",
        1,
    ),
)
def test_requires_snapshot_object(
    payload: object,
) -> None:
    with pytest.raises(
        ValueError,
        match="snapshot must be an object",
    ):
        KnowledgeGraphSnapshotLoader().from_dict(
            payload
        )


@pytest.mark.parametrize(
    "schema_version",
    (
        None,
        True,
        "1",
        2,
    ),
)
def test_requires_snapshot_schema_v1(
    schema_version: object,
) -> None:
    payload = build_payload()
    payload["schema_version"] = (
        schema_version
    )

    with pytest.raises(
        ValueError,
        match=(
            "snapshot.schema_version "
            "must be 1"
        ),
    ):
        KnowledgeGraphSnapshotLoader().from_dict(
            payload
        )


def test_rejects_missing_snapshot_field(
) -> None:
    payload = build_payload()
    del payload["items"]

    with pytest.raises(
        ValueError,
        match="missing snapshot fields: items",
    ):
        KnowledgeGraphSnapshotLoader().from_dict(
            payload
        )


def test_rejects_unknown_snapshot_field(
) -> None:
    payload = build_payload()
    payload["unknown"] = True

    with pytest.raises(
        ValueError,
        match="unknown snapshot fields: unknown",
    ):
        KnowledgeGraphSnapshotLoader().from_dict(
            payload
        )


@pytest.mark.parametrize(
    ("field_name", "value"),
    (
        ("items", None),
        ("items", {}),
        ("relations", None),
        ("relations", {}),
    ),
)
def test_requires_snapshot_arrays(
    field_name: str,
    value: object,
) -> None:
    payload = build_payload()
    payload[field_name] = value

    with pytest.raises(
        ValueError,
        match=(
            f"snapshot.{field_name} "
            "must be an array"
        ),
    ):
        KnowledgeGraphSnapshotLoader().from_dict(
            payload
        )


def test_requires_item_object() -> None:
    payload = build_payload()
    payload["items"] = [None]
    payload["relations"] = []

    with pytest.raises(
        ValueError,
        match=(
            r"snapshot\.items\[0\] "
            "must be an object"
        ),
    ):
        KnowledgeGraphSnapshotLoader().from_dict(
            payload
        )


def test_rejects_missing_item_field(
) -> None:
    payload = build_payload()
    item = payload["items"][0]
    del item["statement"]

    with pytest.raises(
        ValueError,
        match=(
            r"missing snapshot\.items\[0\] "
            "fields: statement"
        ),
    ):
        KnowledgeGraphSnapshotLoader().from_dict(
            payload
        )


def test_rejects_unknown_item_field(
) -> None:
    payload = build_payload()
    payload["items"][0]["unknown"] = True

    with pytest.raises(
        ValueError,
        match=(
            r"unknown snapshot\.items\[0\] "
            "fields: unknown"
        ),
    ):
        KnowledgeGraphSnapshotLoader().from_dict(
            payload
        )


@pytest.mark.parametrize(
    "field_name",
    (
        "applicability",
        "limitations",
        "supporting_findings",
    ),
)
def test_requires_item_arrays(
    field_name: str,
) -> None:
    payload = build_payload()
    payload["items"][0][field_name] = {}

    with pytest.raises(
        ValueError,
        match=(
            rf"snapshot\.items\[0\]\."
            f"{field_name} must be an array"
        ),
    ):
        KnowledgeGraphSnapshotLoader().from_dict(
            payload
        )


def test_requires_provenance_object(
) -> None:
    payload = build_payload()
    payload["items"][0]["provenance"] = []

    with pytest.raises(
        ValueError,
        match=(
            r"snapshot\.items\[0\]\."
            "provenance must be an object"
        ),
    ):
        KnowledgeGraphSnapshotLoader().from_dict(
            payload
        )


@pytest.mark.parametrize(
    "fingerprint",
    (
        None,
        1,
        True,
    ),
)
def test_requires_item_fingerprint_string(
    fingerprint: object,
) -> None:
    payload = build_payload()
    payload["items"][0]["fingerprint"] = (
        fingerprint
    )

    with pytest.raises(
        ValueError,
        match=(
            r"snapshot\.items\[0\]\."
            "fingerprint must be a string"
        ),
    ):
        KnowledgeGraphSnapshotLoader().from_dict(
            payload
        )


def test_rejects_item_fingerprint_mismatch(
) -> None:
    payload = build_payload()
    payload["items"][0]["fingerprint"] = (
        "0" * 64
    )

    with pytest.raises(
        ValueError,
        match=(
            r"snapshot\.items\[0\]\."
            "fingerprint must match"
        ),
    ):
        KnowledgeGraphSnapshotLoader().from_dict(
            payload
        )


def test_requires_relation_object(
) -> None:
    payload = build_payload()
    payload["relations"] = [None]

    with pytest.raises(
        ValueError,
        match=(
            r"snapshot\.relations\[0\] "
            "must be an object"
        ),
    ):
        KnowledgeGraphSnapshotLoader().from_dict(
            payload
        )


def test_rejects_missing_relation_field(
) -> None:
    payload = build_payload()
    del payload["relations"][0][
        "relation_type"
    ]

    with pytest.raises(
        ValueError,
        match=(
            r"missing snapshot\.relations\[0\] "
            "fields: relation_type"
        ),
    ):
        KnowledgeGraphSnapshotLoader().from_dict(
            payload
        )


def test_rejects_unknown_relation_field(
) -> None:
    payload = build_payload()
    payload["relations"][0][
        "unknown"
    ] = True

    with pytest.raises(
        ValueError,
        match=(
            r"unknown snapshot\.relations\[0\] "
            "fields: unknown"
        ),
    ):
        KnowledgeGraphSnapshotLoader().from_dict(
            payload
        )


@pytest.mark.parametrize(
    "endpoint_name",
    (
        "source",
        "target",
    ),
)
def test_requires_endpoint_object(
    endpoint_name: str,
) -> None:
    payload = build_payload()
    payload["relations"][0][
        endpoint_name
    ] = None

    with pytest.raises(
        ValueError,
        match=(
            rf"snapshot\.relations\[0\]\."
            f"{endpoint_name} must be an object"
        ),
    ):
        KnowledgeGraphSnapshotLoader().from_dict(
            payload
        )


def test_rejects_unknown_endpoint_field(
) -> None:
    payload = build_payload()
    payload["relations"][0][
        "source"
    ]["unknown"] = True

    with pytest.raises(
        ValueError,
        match=(
            r"unknown snapshot\.relations\[0\]\."
            "source fields: unknown"
        ),
    ):
        KnowledgeGraphSnapshotLoader().from_dict(
            payload
        )


@pytest.mark.parametrize(
    ("field_name", "value", "message"),
    (
        (
            "id",
            None,
            "id must be a string",
        ),
        (
            "version",
            True,
            "version must be an integer",
        ),
        (
            "fingerprint",
            None,
            "fingerprint must be a string",
        ),
    ),
)
def test_validates_endpoint_reference_types(
    field_name: str,
    value: object,
    message: str,
) -> None:
    payload = build_payload()
    payload["relations"][0][
        "source"
    ][field_name] = value

    with pytest.raises(
        ValueError,
        match=message,
    ):
        KnowledgeGraphSnapshotLoader().from_dict(
            payload
        )


@pytest.mark.parametrize(
    "field_name",
    (
        "id",
        "version",
        "fingerprint",
    ),
)
def test_rejects_dangling_endpoint_reference(
    field_name: str,
) -> None:
    payload = build_payload()
    endpoint = payload["relations"][0][
        "source"
    ]

    if field_name == "version":
        endpoint[field_name] = 999
    else:
        endpoint[field_name] = "missing"

    with pytest.raises(
        ValueError,
        match=(
            r"snapshot\.relations\[0\]\."
            "source must reference an exact "
            "snapshot item"
        ),
    ):
        KnowledgeGraphSnapshotLoader().from_dict(
            payload
        )


@pytest.mark.parametrize(
    "relation_type",
    (
        None,
        1,
        True,
    ),
)
def test_requires_relation_type_string(
    relation_type: object,
) -> None:
    payload = build_payload()
    payload["relations"][0][
        "relation_type"
    ] = relation_type

    with pytest.raises(
        ValueError,
        match=(
            r"snapshot\.relations\[0\]\."
            "relation_type must be a string"
        ),
    ):
        KnowledgeGraphSnapshotLoader().from_dict(
            payload
        )


def test_rejects_unknown_relation_type(
) -> None:
    payload = build_payload()
    payload["relations"][0][
        "relation_type"
    ] = "unknown"

    with pytest.raises(
        ValueError,
        match=(
            r"snapshot\.relations\[0\]\."
            "relation_type is not supported"
        ),
    ):
        KnowledgeGraphSnapshotLoader().from_dict(
            payload
        )


def test_rejects_invalid_json(
    tmp_path: Path,
) -> None:
    path = tmp_path / "snapshot.json"
    path.write_text(
        "{invalid",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match=(
            "invalid knowledge graph "
            "snapshot JSON"
        ),
    ):
        KnowledgeGraphSnapshotLoader().load(
            path
        )


def test_reports_unreadable_file(
    tmp_path: Path,
) -> None:
    path = tmp_path / "missing.json"

    with pytest.raises(
        ValueError,
        match=(
            "unable to read knowledge graph "
            "snapshot file"
        ),
    ):
        KnowledgeGraphSnapshotLoader().load(
            path
        )


def test_rejects_duplicate_items(
) -> None:
    payload = build_payload()
    payload["items"].append(
        deepcopy(payload["items"][0])
    )

    with pytest.raises(
        ValueError,
        match=(
            "items must not contain duplicate "
            "fingerprints"
        ),
    ):
        KnowledgeGraphSnapshotLoader().from_dict(
            payload
        )
