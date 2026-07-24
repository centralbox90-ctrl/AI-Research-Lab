from __future__ import annotations

import json
from hashlib import sha256

from src.research.evidence import Evidence
from src.research.finding import Finding


class FindingEvaluator:
    """
    Converts Evidence into a reproducible scientific Finding.
    """

    DEFAULT_PIPELINE_VERSION = "finding-v1"

    def evaluate(
        self,
        *,
        evidence: Evidence,
        statement: str,
        applicable_markets: tuple[str, ...],
        analysis_pipeline_version: str = (
            DEFAULT_PIPELINE_VERSION
        ),
    ) -> Finding:
        if not isinstance(evidence, Evidence):
            raise TypeError(
                "evidence must be an Evidence"
            )

        normalized_pipeline_version = (
            self._normalize_text(
                analysis_pipeline_version,
                field_name=(
                    "analysis_pipeline_version"
                ),
            )
        )
        provenance = (
            (
                "analysis_pipeline_version",
                normalized_pipeline_version,
            ),
            (
                "evidence_direction",
                evidence.direction.value,
            ),
            (
                "evidence_fingerprint",
                evidence.fingerprint,
            ),
            (
                "evidence_id",
                evidence.id,
            ),
            (
                "evidence_strength",
                evidence.strength.value,
            ),
            *tuple(
                (
                    f"evidence.{key}",
                    value,
                )
                for key, value
                in evidence.provenance
            ),
        )
        prototype = Finding(
            id="pending",
            hypothesis_id=evidence.hypothesis_id,
            statement=statement,
            confidence=evidence.confidence,
            applicable_markets=applicable_markets,
            limitations=evidence.limitations,
            supporting_evidence=(evidence.id,),
            provenance=provenance,
        )
        finding_id = self._build_finding_id(
            prototype
        )

        return Finding(
            id=finding_id,
            hypothesis_id=prototype.hypothesis_id,
            statement=prototype.statement,
            confidence=prototype.confidence,
            applicable_markets=(
                prototype.applicable_markets
            ),
            limitations=prototype.limitations,
            supporting_evidence=(
                prototype.supporting_evidence
            ),
            provenance=prototype.provenance,
        )

    @staticmethod
    def _build_finding_id(
        finding: Finding,
    ) -> str:
        payload = finding.to_dict()
        del payload["id"]

        serialized = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )
        digest = sha256(
            serialized.encode("utf-8")
        ).hexdigest()

        return f"finding:sha256:{digest}"

    @staticmethod
    def _normalize_text(
        value: object,
        *,
        field_name: str,
    ) -> str:
        if not isinstance(value, str):
            raise TypeError(
                f"{field_name} must be a string"
            )

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                f"{field_name} must not be empty"
            )

        return normalized