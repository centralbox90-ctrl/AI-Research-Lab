from datetime import datetime, timedelta, timezone

import pytest

from src.application.research_artifact_envelope import (
    ResearchArtifactEnvelope,
    ResearchArtifactEnvelopeFactory,
    ResearchArtifactSourceReference,
    fingerprint_research_artifact_payload,
    is_research_artifact_envelope,
    load_research_artifact_envelope,
)


CREATED_AT = datetime(
    2026,
    7,
    28,
    12,
    0,
    tzinfo=timezone.utc,
)


class FixedClock:
    def now(self) -> datetime:
        return CREATED_AT


class FixedIdGenerator:
    def generate(self) -> str:
        return "artifact-001"


def build_factory() -> ResearchArtifactEnvelopeFactory:
    return ResearchArtifactEnvelopeFactory(
        producer="market-research",
        producer_version="git:abc123",
        clock=FixedClock(),
        id_generator=FixedIdGenerator(),
    )


def build_payload() -> dict[str, object]:
    return {
        "artifact_version": 1,
        "cycle": {
            "result": {
                "id": "result-001",
                "success": True,
            },
        },
    }


def build_reference() -> (
    ResearchArtifactSourceReference
):
    return ResearchArtifactSourceReference(
        reference_type="experiment_execution",
        reference_id="execution-001",
        reference_fingerprint="a" * 64,
    )


def test_factory_creates_complete_envelope() -> None:
    payload = build_payload()
    reference = build_reference()

    envelope = build_factory().create(
        artifact_type="market_research_cycle",
        payload_schema_version=1,
        correlation_id="research-001",
        source_references=(reference,),
        provenance={
            "specification_fingerprint": "b" * 64,
        },
        payload=payload,
    )

    assert envelope.schema_version == 1
    assert envelope.artifact_id == "artifact-001"
    assert envelope.created_at == CREATED_AT
    assert envelope.producer == "market-research"
    assert envelope.producer_version == "git:abc123"
    assert envelope.correlation_id == "research-001"
    assert envelope.source_references == (
        reference,
    )
    assert envelope.payload_fingerprint == (
        fingerprint_research_artifact_payload(
            payload
        )
    )


def test_to_dict_returns_json_compatible_values() -> None:
    envelope = build_factory().create(
        artifact_type="market_research_cycle",
        payload_schema_version=1,
        source_references=(build_reference(),),
        provenance={
            "random_seed": 42,
            "tags": ("market", "test"),
        },
        payload=build_payload(),
    )

    serialized = envelope.to_dict()

    assert serialized["created_at"] == (
        "2026-07-28T12:00:00+00:00"
    )
    assert serialized["source_references"] == [
        {
            "reference_type": (
                "experiment_execution"
            ),
            "reference_id": "execution-001",
            "reference_version": None,
            "reference_fingerprint": "a" * 64,
        },
    ]
    assert serialized["provenance"]["tags"] == [
        "market",
        "test",
    ]


def test_payload_is_an_immutable_snapshot() -> None:
    payload = build_payload()

    envelope = build_factory().create(
        artifact_type="market_research_cycle",
        payload_schema_version=1,
        provenance={},
        payload=payload,
    )

    payload["cycle"]["result"]["id"] = "changed"

    assert envelope.to_dict()["payload"][
        "cycle"
    ]["result"]["id"] == "result-001"

    with pytest.raises(TypeError):
        envelope.payload["new"] = True


def test_payload_fingerprint_is_canonical() -> None:
    first = {
        "b": 2,
        "a": {
            "value": 1,
        },
    }
    second = {
        "a": {
            "value": 1,
        },
        "b": 2,
    }

    assert (
        fingerprint_research_artifact_payload(first)
        == fingerprint_research_artifact_payload(
            second
        )
    )


def test_rejects_payload_fingerprint_mismatch() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "payload_fingerprint does not "
            "match payload"
        ),
    ):
        ResearchArtifactEnvelope(
            schema_version=1,
            artifact_type="market_research_cycle",
            payload_schema_version=1,
            artifact_id="artifact-001",
            created_at=CREATED_AT,
            producer="market-research",
            producer_version="git:abc123",
            correlation_id=None,
            source_references=(),
            provenance={},
            payload_fingerprint="0" * 64,
            payload=build_payload(),
        )


def test_rejects_duplicate_source_references() -> None:
    reference = build_reference()

    with pytest.raises(
        ValueError,
        match="source_references must be unique",
    ):
        build_factory().create(
            artifact_type="market_research_cycle",
            payload_schema_version=1,
            source_references=(
                reference,
                reference,
            ),
            provenance={},
            payload=build_payload(),
        )


@pytest.mark.parametrize(
    "payload, error_type, message",
    (
        (
            {"value": float("nan")},
            ValueError,
            "non-finite number",
        ),
        (
            {"value": object()},
            TypeError,
            "non-JSON value",
        ),
        (
            {1: "value"},
            TypeError,
            "non-string key",
        ),
    ),
)
def test_rejects_invalid_json_payload(
    payload: dict[object, object],
    error_type: type[Exception],
    message: str,
) -> None:
    with pytest.raises(
        error_type,
        match=message,
    ):
        fingerprint_research_artifact_payload(
            payload
        )


def test_normalizes_created_at_to_utc() -> None:
    local_time = datetime(
        2026,
        7,
        28,
        14,
        0,
        tzinfo=timezone(
            timedelta(hours=2)
        ),
    )
    payload = build_payload()

    envelope = ResearchArtifactEnvelope(
        schema_version=1,
        artifact_type="market_research_cycle",
        payload_schema_version=1,
        artifact_id="artifact-001",
        created_at=local_time,
        producer="market-research",
        producer_version="git:abc123",
        correlation_id=None,
        source_references=(),
        provenance={},
        payload_fingerprint=(
            fingerprint_research_artifact_payload(
                payload
            )
        ),
        payload=payload,
    )

    assert envelope.created_at == CREATED_AT


def test_rejects_naive_created_at() -> None:
    payload = build_payload()

    with pytest.raises(
        ValueError,
        match="created_at must be timezone-aware",
    ):
        ResearchArtifactEnvelope(
            schema_version=1,
            artifact_type="market_research_cycle",
            payload_schema_version=1,
            artifact_id="artifact-001",
            created_at=datetime(
                2026,
                7,
                28,
                12,
                0,
            ),
            producer="market-research",
            producer_version="git:abc123",
            correlation_id=None,
            source_references=(),
            provenance={},
            payload_fingerprint=(
                fingerprint_research_artifact_payload(
                    payload
                )
            ),
            payload=payload,
        )


def test_loader_round_trips_and_validates_envelope(
) -> None:
    original = build_factory().create(
        artifact_type="market_research_cycle",
        payload_schema_version=1,
        correlation_id="research-001",
        source_references=(build_reference(),),
        provenance={
            "code_version": "git:abc123",
        },
        payload=build_payload(),
    )
    serialized = original.to_dict()

    loaded = load_research_artifact_envelope(
        serialized
    )

    assert loaded.to_dict() == serialized
    assert is_research_artifact_envelope(
        serialized
    )
    assert not is_research_artifact_envelope(
        build_payload()
    )


def test_loader_rejects_changed_payload() -> None:
    serialized = build_factory().create(
        artifact_type="market_research_cycle",
        payload_schema_version=1,
        provenance={},
        payload=build_payload(),
    ).to_dict()

    serialized["payload"]["cycle"]["result"][
        "id"
    ] = "changed"

    with pytest.raises(
        ValueError,
        match=(
            "payload_fingerprint does not "
            "match payload"
        ),
    ):
        load_research_artifact_envelope(
            serialized
        )


def test_loader_rejects_unknown_envelope_fields(
) -> None:
    serialized = build_factory().create(
        artifact_type="market_research_cycle",
        payload_schema_version=1,
        provenance={},
        payload=build_payload(),
    ).to_dict()
    serialized["unexpected"] = True

    with pytest.raises(
        ValueError,
        match=(
            "serialized envelope has unknown "
            "fields: unexpected"
        ),
    ):
        load_research_artifact_envelope(
            serialized
        )


def test_validates_source_reference_version() -> None:
    with pytest.raises(
        ValueError,
        match="reference_version must be positive",
    ):
        ResearchArtifactSourceReference(
            reference_type="knowledge_revision",
            reference_id="knowledge-001",
            reference_version=0,
        )
