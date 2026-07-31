from __future__ import annotations

from datetime import datetime, timezone

import pytest

from src.application.get_stored_research_artifact import (
    GetStoredResearchArtifact,
    StoredResearchArtifactIntegrityError,
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


def build_payload(
    result_id: str = "result-001",
) -> dict[str, object]:
    return {
        "artifact_version": 1,
        "specification": {},
        "cycle": {
            "result": {
                "id": result_id,
            },
            "evaluation": {},
            "statistical_evaluation": {},
            "robustness_evaluation": {},
            "contradiction_evaluation": {},
            "evidence_strength_evaluation": {},
            "hypothesis_decision": {},
            "next_experiment_selection": {},
            "evidence": {},
            "analysis": {},
            "conclusion": {},
            "knowledge": {},
        },
    }


def build_envelope(
    payload: dict[str, object] | None = None,
) -> dict[str, object]:
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
        payload=(
            build_payload()
            if payload is None
            else payload
        ),
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
        StoredResearchArtifactIntegrityError,
        match=(
            "market_research_cycle result id does "
            "not match storage key"
        ),
    ) as error:
        application.execute("result-other")

    assert error.value.result_id == "result-other"
    assert error.value.reason == (
        "market_research_cycle result id does "
        "not match storage key"
    )
    assert isinstance(
        error.value.__cause__,
        ValueError,
    )


def test_rejects_market_research_cycle_with_missing_payload_field(
) -> None:
    payload = build_payload()
    del payload["specification"]
    application = GetStoredResearchArtifact(
        store=StubStore(
            build_envelope(payload)
        )
    )

    with pytest.raises(
        ValueError,
        match=(
            "market_research_cycle payload is "
            "missing fields: specification"
        ),
    ):
        application.execute("result-001")


def test_rejects_market_research_cycle_with_unknown_payload_field(
) -> None:
    payload = build_payload()
    payload["unexpected"] = "value"
    application = GetStoredResearchArtifact(
        store=StubStore(
            build_envelope(payload)
        )
    )

    with pytest.raises(
        ValueError,
        match=(
            "market_research_cycle payload has "
            "unknown fields: unexpected"
        ),
    ):
        application.execute("result-001")


def test_rejects_market_research_cycle_with_incomplete_cycle(
) -> None:
    payload = build_payload()
    del payload["cycle"]["analysis"]
    application = GetStoredResearchArtifact(
        store=StubStore(
            build_envelope(payload)
        )
    )

    with pytest.raises(
        ValueError,
        match=(
            "market_research_cycle cycle is "
            "missing fields: analysis"
        ),
    ):
        application.execute("result-001")


def test_rejects_market_research_cycle_with_invalid_optional_section(
) -> None:
    payload = build_payload()
    payload["metadata"] = []
    application = GetStoredResearchArtifact(
        store=StubStore(
            build_envelope(payload)
        )
    )

    with pytest.raises(
        ValueError,
        match=(
            "market_research_cycle payload field "
            "metadata must be an object"
        ),
    ):
        application.execute("result-001")


def test_rejects_legacy_artifact_storage_identity_mismatch(
) -> None:
    legacy = {
        "artifact_version": 1,
        "cycle": {
            "result": {
                "id": "result-payload",
            },
        },
    }
    application = GetStoredResearchArtifact(
        store=StubStore(legacy)
    )

    with pytest.raises(
        ValueError,
        match=(
            "legacy research cycle result id does "
            "not match storage key"
        ),
    ):
        application.execute("result-storage")


def test_rejects_legacy_cycle_with_invalid_section(
) -> None:
    legacy = {
        "result": {
            "id": "result-legacy",
        },
        "hypothesis_decision": [],
    }
    application = GetStoredResearchArtifact(
        store=StubStore(legacy)
    )

    with pytest.raises(
        ValueError,
        match=(
            "legacy research cycle field "
            "hypothesis_decision must be an object"
        ),
    ):
        application.execute("result-legacy")


def test_rejects_legacy_cycle_with_unknown_field(
) -> None:
    legacy = {
        "result": {
            "id": "result-legacy",
        },
        "unexpected": {},
    }
    application = GetStoredResearchArtifact(
        store=StubStore(legacy)
    )

    with pytest.raises(
        ValueError,
        match=(
            "legacy research cycle has "
            "unknown fields: unexpected"
        ),
    ):
        application.execute("result-legacy")


def test_rejects_legacy_artifact_with_invalid_history(
) -> None:
    legacy = {
        "artifact_version": 1,
        "cycle": {
            "result": {
                "id": "result-legacy",
            },
        },
        "history": [
            "invalid-event",
        ],
    }
    application = GetStoredResearchArtifact(
        store=StubStore(legacy)
    )

    with pytest.raises(
        ValueError,
        match=(
            "legacy market research history "
            "must be an array of objects"
        ),
    ):
        application.execute("result-legacy")
