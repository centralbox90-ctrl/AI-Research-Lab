from datetime import datetime, timezone

from src.application.artifact_comparison_input_extractor import (
    ArtifactComparisonInputExtractor,
)
from src.application.research_artifact_envelope import (
    ResearchArtifactEnvelope,
    fingerprint_research_artifact_payload,
)


def build_artifact(
    artifact_id: str,
    hypothesis_description: str,
    evidence: dict,
    confidence: float,
) -> dict:
    return {
        "metadata": {
            "artifact_id": artifact_id,
        },
        "specification": {
            "hypothesis_title": "Test hypothesis",
            "hypothesis_description": (
                hypothesis_description
            ),
        },
        "cycle": {
            "evidence": {
                "data": evidence,
            },
            "evidence_strength_evaluation": {
                "score": confidence,
            },
        },
    }


def test_artifact_comparison_input_extractor():

    extractor = ArtifactComparisonInputExtractor()

    artifact_a = build_artifact(
        artifact_id="artifact-001",
        hypothesis_description=(
            "Williams predicts reversal"
        ),
        evidence={
            "sample_size": 500,
            "markets": 1,
        },
        confidence=0.45,
    )

    artifact_b = build_artifact(
        artifact_id="artifact-002",
        hypothesis_description=(
            "Williams plus ADX predicts reversal"
        ),
        evidence={
            "sample_size": 5000,
            "markets": 5,
        },
        confidence=0.72,
    )

    result = extractor.extract(
        artifact_a=artifact_a,
        artifact_b=artifact_b,
    )

    assert result["artifact_a_id"] == "artifact-001"
    assert result["artifact_b_id"] == "artifact-002"

    assert (
        result["previous_hypothesis"]
        == "Williams predicts reversal"
    )

    assert (
        result["current_hypothesis"]
        == "Williams plus ADX predicts reversal"
    )

    assert (
        result["hypothesis_change_reason"]
        == "Hypothesis changed between research artifacts."
    )

    assert result["previous_evidence"] == {
        "sample_size": 500,
        "markets": 1,
    }

    assert result["current_evidence"] == {
        "sample_size": 5000,
        "markets": 5,
    }

    assert (
        result["evidence_change_reason"]
        == "Evidence changed between research artifacts."
    )

    assert result["previous_confidence"] == 0.45
    assert result["current_confidence"] == 0.72

    assert (
        result["confidence_change_reason"]
        == "Confidence increased."
    )

def test_extracts_legacy_and_enveloped_artifacts() -> None:
    legacy = build_artifact(
        artifact_id="legacy-artifact",
        hypothesis_description=(
            "Williams predicts reversal"
        ),
        evidence={
            "sample_size": 500,
        },
        confidence=0.45,
    )
    payload = build_artifact(
        artifact_id="inner-compatibility-id",
        hypothesis_description=(
            "Williams plus ADX predicts reversal"
        ),
        evidence={
            "sample_size": 5000,
        },
        confidence=0.72,
    )
    enveloped = ResearchArtifactEnvelope(
        schema_version=1,
        artifact_type="market_research_cycle",
        payload_schema_version=1,
        artifact_id="envelope-artifact",
        created_at=datetime(
            2026,
            7,
            28,
            12,
            0,
            tzinfo=timezone.utc,
        ),
        producer="market_research_application",
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
    ).to_dict()

    result = ArtifactComparisonInputExtractor().extract(
        artifact_a=legacy,
        artifact_b=enveloped,
    )

    assert result["artifact_a_id"] == (
        "legacy-artifact"
    )
    assert result["artifact_b_id"] == (
        "envelope-artifact"
    )
    assert result["previous_confidence"] == 0.45
    assert result["current_confidence"] == 0.72
    assert result["confidence_change_reason"] == (
        "Confidence increased."
    )
