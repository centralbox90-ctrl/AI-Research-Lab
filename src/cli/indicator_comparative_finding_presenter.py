from __future__ import annotations

from src.research.finding import Finding


def present_indicator_comparative_finding(
    finding: Finding,
) -> dict[str, object]:
    """Build a JSON-compatible comparative Finding payload."""

    if not isinstance(finding, Finding):
        raise TypeError(
            "finding must be a Finding"
        )

    presented_finding = finding.to_dict()
    presented_finding["fingerprint"] = (
        finding.fingerprint
    )

    return {
        "artifact_type": (
            "indicator_comparative_finding"
        ),
        "artifact_version": 1,
        "finding": presented_finding,
    }