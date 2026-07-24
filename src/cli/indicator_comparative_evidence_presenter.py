from __future__ import annotations

from src.research.evidence import Evidence


def present_indicator_comparative_evidence(
    evidence: Evidence,
) -> dict[str, object]:
    """Build a JSON-compatible comparative Evidence payload."""

    if not isinstance(evidence, Evidence):
        raise TypeError(
            "evidence must be an Evidence"
        )

    presented_evidence = evidence.to_dict()
    presented_evidence["fingerprint"] = (
        evidence.fingerprint
    )

    return {
        "artifact_type": (
            "indicator_comparative_evidence"
        ),
        "artifact_version": 1,
        "evidence": presented_evidence,
    }