from dataclasses import replace

import pytest

from src.research.evidence import (
    Evidence,
    EvidenceDirection,
    EvidenceStrength,
)
from src.research.finding import (
    Finding,
    FindingRelationship,
)
from src.research.finding_evaluator import (
    FindingEvaluator,
)


def build_evidence(
    **overrides: object,
) -> Evidence:
    values: dict[str, object] = {
        "id": "evidence:sha256:example",
        "hypothesis_id": "hypothesis-rsi",
        "observation_refs": (
            "dataset-a:horizon:3",
            "dataset-b:horizon:3",
        ),
        "direction": EvidenceDirection.SUPPORTING,
        "strength": EvidenceStrength.STRONG,
        "confidence": 0.95,
        "consistency": 1.0,
        "robustness": 1.0,
        "provenance": (
            ("method", "moving_block_bootstrap"),
            ("research_fingerprint", "research-1"),
        ),
        "applicability": (
            "indicator:rsi",
            "symbol:EURUSD",
            "timeframe:H1",
            "horizon:3",
        ),
        "limitations": (
            "limited to historical datasets",
        ),
    }
    values.update(overrides)

    return Evidence(**values)  # type: ignore[arg-type]


def evaluate(
    *,
    evidence: object | None = None,
    statement: object = (
        "RSI improves entries on EURUSD H1."
    ),
    applicable_markets: object = (
        "EURUSD:H1",
        "GBPUSD:H1",
    ),
    analysis_pipeline_version: object = (
        "finding-v1"
    ),
) -> Finding:
    selected_evidence = (
        build_evidence()
        if evidence is None
        else evidence
    )

    return FindingEvaluator().evaluate(
        evidence=selected_evidence,  # type: ignore[arg-type]
        statement=statement,  # type: ignore[arg-type]
        applicable_markets=(  # type: ignore[arg-type]
            applicable_markets
        ),
        analysis_pipeline_version=(  # type: ignore[arg-type]
            analysis_pipeline_version
        ),
    )


def test_builds_finding_from_evidence() -> None:
    evidence = build_evidence()
    finding = evaluate(
        evidence=evidence,
        statement=(
            "  RSI improves entries on EURUSD H1.  "
        ),
        applicable_markets=(
            "GBPUSD:H1",
            " EURUSD:H1 ",
        ),
        analysis_pipeline_version=" analysis-v1 ",
    )

    assert finding.id.startswith(
        "finding:sha256:"
    )
    assert len(finding.id) == (
        len("finding:sha256:") + 64
    )
    assert finding.hypothesis_id == (
        evidence.hypothesis_id
    )
    assert finding.relationship is (
        FindingRelationship.SUPPORTING
    )
    assert finding.statement == (
        "RSI improves entries on EURUSD H1."
    )
    assert finding.confidence == evidence.confidence
    assert finding.applicable_markets == (
        "EURUSD:H1",
        "GBPUSD:H1",
    )
    assert finding.limitations == (
        evidence.limitations
    )
    assert finding.supporting_evidence == (
        evidence.id,
    )

    provenance = dict(finding.provenance)

    assert provenance[
        "analysis_pipeline_version"
    ] == "analysis-v1"
    assert provenance["evidence_id"] == evidence.id
    assert provenance[
        "evidence_fingerprint"
    ] == evidence.fingerprint
    assert provenance[
        "evidence_direction"
    ] == "supporting"
    assert provenance[
        "evidence_strength"
    ] == "strong"
    assert provenance["evidence.method"] == (
        "moving_block_bootstrap"
    )


@pytest.mark.parametrize(
    ("direction", "relationship"),
    (
        (
            EvidenceDirection.SUPPORTING,
            FindingRelationship.SUPPORTING,
        ),
        (
            EvidenceDirection.CONTRADICTORY,
            FindingRelationship.CONTRADICTORY,
        ),
        (
            EvidenceDirection.INCONCLUSIVE,
            FindingRelationship.INCONCLUSIVE,
        ),
    ),
)
def test_maps_evidence_direction_to_relationship(
    direction: EvidenceDirection,
    relationship: FindingRelationship,
) -> None:
    finding = evaluate(
        evidence=build_evidence(
            direction=direction,
        ),
    )

    assert finding.relationship is relationship


def test_is_deterministic_and_order_independent(
) -> None:
    first = evaluate(
        applicable_markets=(
            "EURUSD:H1",
            "GBPUSD:H1",
        ),
    )
    second = evaluate(
        applicable_markets=(
            "GBPUSD:H1",
            "EURUSD:H1",
        ),
    )

    assert first == second
    assert first.id == second.id
    assert first.fingerprint == second.fingerprint


@pytest.mark.parametrize(
    "field_name",
    (
        "statement",
        "analysis_pipeline_version",
    ),
)
def test_identity_changes_with_interpretation_context(
    field_name: str,
) -> None:
    original = evaluate()

    if field_name == "statement":
        changed = evaluate(
            statement="A different interpretation."
        )
    else:
        changed = evaluate(
            analysis_pipeline_version="finding-v2"
        )

    assert changed.id != original.id
    assert changed.fingerprint != original.fingerprint


def test_identity_changes_with_evidence() -> None:
    evidence = build_evidence()
    changed_evidence = replace(
        evidence,
        confidence=0.7,
    )

    assert evaluate(
        evidence=evidence
    ).id != evaluate(
        evidence=changed_evidence
    ).id


def test_preserves_inconclusive_evidence_context(
) -> None:
    evidence = build_evidence(
        direction=EvidenceDirection.INCONCLUSIVE,
        strength=EvidenceStrength.NONE,
        confidence=0.0,
        limitations=(
            "insufficient replications",
        ),
    )
    finding = evaluate(
        evidence=evidence,
        statement=(
            "Available evidence is inconclusive."
        ),
    )

    assert finding.confidence == 0.0
    assert finding.limitations == (
        "insufficient replications",
    )
    assert dict(finding.provenance)[
        "evidence_direction"
    ] == "inconclusive"


def test_rejects_non_evidence() -> None:
    with pytest.raises(
        TypeError,
        match="evidence must be an Evidence",
    ):
        evaluate(evidence=object())


@pytest.mark.parametrize(
    ("value", "error_type", "message"),
    (
        (
            object(),
            TypeError,
            "analysis_pipeline_version must be a string",
        ),
        (
            " ",
            ValueError,
            "analysis_pipeline_version must not be empty",
        ),
    ),
)
def test_rejects_invalid_pipeline_version(
    value: object,
    error_type: type[Exception],
    message: str,
) -> None:
    with pytest.raises(error_type, match=message):
        evaluate(
            analysis_pipeline_version=value
        )


def test_rejects_invalid_statement() -> None:
    with pytest.raises(
        ValueError,
        match="statement must not be empty",
    ):
        evaluate(statement=" ")


def test_rejects_invalid_markets() -> None:
    with pytest.raises(
        ValueError,
        match="applicable_markets must not be empty",
    ):
        evaluate(applicable_markets=())