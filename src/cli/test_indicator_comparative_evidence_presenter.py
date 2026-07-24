import json

import pytest

from src.cli.indicator_comparative_evidence_presenter import (
    present_indicator_comparative_evidence,
)
from src.research.evidence import (
    Evidence,
    EvidenceDirection,
    EvidenceStrength,
)


def build_evidence() -> Evidence:
    return Evidence(
        id="evidence-id",
        hypothesis_id="hypothesis-id",
        observation_refs=(
            "dataset-a:horizon:3",
            "dataset-b:horizon:3",
        ),
        direction=EvidenceDirection.INCONCLUSIVE,
        strength=EvidenceStrength.WEAK,
        confidence=0.5,
        consistency=1.0,
        robustness=1.0,
        provenance=(
            (
                "research_fingerprint",
                "research-id",
            ),
            (
                "evaluation_plan_fingerprint",
                "plan-id",
            ),
            (
                "horizon",
                "3",
            ),
            (
                "dataset_ids",
                '["dataset-a","dataset-b"]',
            ),
        ),
        applicability=(
            "indicator:rsi",
            "symbol:EURUSD",
            "timeframe:H1",
            "horizon:3",
        ),
        limitations=(
            "supporting replications 1 below required 2",
        ),
    )


def test_presents_json_compatible_evidence(
) -> None:
    evidence = build_evidence()
    payload = (
        present_indicator_comparative_evidence(
            evidence
        )
    )
    serialized = json.loads(
        json.dumps(
            payload,
            sort_keys=True,
        )
    )

    assert serialized["artifact_type"] == (
        "indicator_comparative_evidence"
    )
    assert serialized["artifact_version"] == 1

    presented = serialized["evidence"]

    assert presented["schema_version"] == 1
    assert presented["id"] == "evidence-id"
    assert presented["fingerprint"] == (
        evidence.fingerprint
    )
    assert presented["hypothesis_id"] == (
        "hypothesis-id"
    )
    assert presented["direction"] == "inconclusive"
    assert presented["strength"] == "weak"
    assert presented["confidence"] == 0.5
    assert presented["consistency"] == 1.0
    assert presented["robustness"] == 1.0
    assert presented["observation_refs"] == [
        "dataset-a:horizon:3",
        "dataset-b:horizon:3",
    ]
    assert presented["provenance"] == {
        "dataset_ids": '["dataset-a","dataset-b"]',
        "evaluation_plan_fingerprint": "plan-id",
        "horizon": "3",
        "research_fingerprint": "research-id",
    }
    assert presented["applicability"] == [
        "indicator:rsi",
        "symbol:EURUSD",
        "timeframe:H1",
        "horizon:3",
    ]
    assert presented["limitations"] == [
        "supporting replications 1 below required 2",
    ]


def test_rejects_invalid_evidence() -> None:
    with pytest.raises(
        TypeError,
        match="evidence must be an Evidence",
    ):
        present_indicator_comparative_evidence(
            object()
        )