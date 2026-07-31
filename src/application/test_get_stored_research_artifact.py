from __future__ import annotations

from datetime import datetime, timezone

import pytest

from src.application.get_stored_research_artifact import (
    GetStoredResearchArtifact,
)
from src.application.research_artifact_envelope import (
    ResearchArtifactEnvelopeFactory,
)


class StubStore:
    def __init__(
        self,
        payload: dict[str, object] | None,
    ) -> None:
        self.payload = payload
        self.calls: list[str] = []

    def get(
        self,
        result_id: str,
    ) -> dict[str, object] | None:
        self.calls.append(result_id)
        return self.payload


class FixedClock:
    def now(self) -> datetime:
        return datetime(
            2026,
            7,
            30,
            12,
            0,
            tzinfo=timezone.utc,
        )


class FixedIdGenerator:
    def generate(self) -> str:
        return "artifact-market-001"


def build_envelope() -> dict[str, object]:
    return ResearchArtifactEnvelopeFactory(
        producer="market-research",
        producer_version="git:test",
        clock=FixedClock(),
        id_generator=FixedIdGenerator(),
    ).create(
        artifact_type="market_research_cycle",
        payload_schema_version=1,
        correlation_id="research-lifecycle-42",
        provenance={
            "code_version": "git:test",
        },
        payload={
            "artifact_version": 1,
            "cycle": {
                "result": {
                    "id": "result-001",
                },
            },
        },
    ).to_dict()


def test_returns_none_when_artifact_is_missing(
) -> None:
    store = StubStore(None)
    application = GetStoredResearchArtifact(
        store=store
    )

    assert application.execute("result-missing") is None
    assert store.calls == ["result-missing"]


def test_preserves_legacy_artifact_compatibility(
) -> None:
    legacy = {
        "artifact_version": 1,
        "cycle": {
            "result": {
                "id": "result-legacy",
            },
        },
    }
    application = GetStoredResearchArtifact(
        store=StubStore(legacy)
    )

    assert application.execute("result-legacy") == legacy


def test_validates_and_returns_stored_envelope(
) -> None:
    serialized = build_envelope()
    application = GetStoredResearchArtifact(
        store=StubStore(serialized)
    )

    assert application.execute("result-001") == serialized


def test_rejects_stored_envelope_with_changed_payload(
) -> None:
    serialized = build_envelope()
    serialized["payload"]["cycle"]["result"][
        "id"
    ] = "result-tampered"
    application = GetStoredResearchArtifact(
        store=StubStore(serialized)
    )

    with pytest.raises(
        ValueError,
        match=(
            "payload_fingerprint does not "
            "match payload"
        ),
    ):
        application.execute("result-001")


def test_rejects_market_research_cycle_with_storage_identity_mismatch(
) -> None:
    serialized = build_envelope()
    application = GetStoredResearchArtifact(
        store=StubStore(serialized)
    )

    with pytest.raises(
        ValueError,
        match=(
            "market_research_cycle result id does "
            "not match storage key"
        ),
    ):
        application.execute("result-other")
