import json

import pytest

from src.cli.indicator_comparative_finding_presenter import (
    present_indicator_comparative_finding,
)
from src.research.finding import Finding


def build_finding() -> Finding:
    return Finding(
        id="finding-id",
        hypothesis_id="hypothesis-id",
        statement=(
            "The replicated effect supports "
            "further investigation."
        ),
        confidence=0.75,
        applicable_markets=(
            "timeframe:H1",
            "symbol:EURUSD",
        ),
        limitations=(
            "limited sample size",
        ),
        supporting_evidence=(
            "evidence-b",
            "evidence-a",
        ),
        provenance=(
            (
                "evidence_fingerprint",
                "evidence-fingerprint",
            ),
            (
                "analysis_pipeline_version",
                "finding-evaluator-v1",
            ),
        ),
    )


def test_presents_json_compatible_finding(
) -> None:
    finding = build_finding()
    payload = (
        present_indicator_comparative_finding(
            finding
        )
    )
    serialized = json.loads(
        json.dumps(
            payload,
            sort_keys=True,
        )
    )

    assert serialized["artifact_type"] == (
        "indicator_comparative_finding"
    )
    assert serialized["artifact_version"] == 1

    presented = serialized["finding"]

    assert presented["schema_version"] == 1
    assert presented["id"] == "finding-id"
    assert presented["fingerprint"] == (
        finding.fingerprint
    )
    assert presented["hypothesis_id"] == (
        "hypothesis-id"
    )
    assert presented["statement"] == (
        "The replicated effect supports "
        "further investigation."
    )
    assert presented["confidence"] == 0.75
    assert presented["applicable_markets"] == [
        "symbol:EURUSD",
        "timeframe:H1",
    ]
    assert presented["limitations"] == [
        "limited sample size",
    ]
    assert presented["supporting_evidence"] == [
        "evidence-a",
        "evidence-b",
    ]
    assert presented["provenance"] == {
        "analysis_pipeline_version": (
            "finding-evaluator-v1"
        ),
        "evidence_fingerprint": (
            "evidence-fingerprint"
        ),
    }


def test_rejects_invalid_finding() -> None:
    with pytest.raises(
        TypeError,
        match="finding must be a Finding",
    ):
        present_indicator_comparative_finding(
            object()
        )