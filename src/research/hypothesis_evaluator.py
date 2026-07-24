from __future__ import annotations

import json
from hashlib import sha256
from math import fsum

from src.research.finding import (
    Finding,
    FindingRelationship,
)
from src.research.hypothesis_evaluation import (
    HypothesisEvaluation,
    HypothesisEvaluationState,
)
from src.research.hypothesis_evaluation_plan import (
    HypothesisEvaluationPlan,
)


class HypothesisEvaluator:
    """
    Evaluates a reproducible set of Findings under a declared plan.
    """

    def __init__(
        self,
        *,
        plan: HypothesisEvaluationPlan,
    ) -> None:
        if not isinstance(
            plan,
            HypothesisEvaluationPlan,
        ):
            raise TypeError(
                "plan must be a "
                "HypothesisEvaluationPlan"
            )

        self._plan = plan

    def evaluate(
        self,
        *,
        findings: tuple[Finding, ...],
    ) -> HypothesisEvaluation:
        normalized_findings = (
            self._normalize_findings(findings)
        )
        hypothesis_id = (
            normalized_findings[0].hypothesis_id
        )

        if any(
            finding.hypothesis_id != hypothesis_id
            for finding in normalized_findings
        ):
            raise ValueError(
                "findings must belong to the same hypothesis"
            )

        confidence = fsum(
            finding.confidence
            for finding in normalized_findings
        ) / len(normalized_findings)

        relationship_counts = {
            relationship: sum(
                finding.relationship is relationship
                for finding in normalized_findings
            )
            for relationship in FindingRelationship
        }
        state = self._select_state(
            finding_count=len(normalized_findings),
            confidence=confidence,
            relationship_counts=(
                relationship_counts
            ),
        )
        rationale = (
            self._rationale_for_state(state),
        )
        limitations = self._build_limitations(
            normalized_findings,
            relationship_counts=(
                relationship_counts
            ),
        )
        provenance = (
            (
                "evaluation_plan_fingerprint",
                self._plan.fingerprint,
            ),
            (
                "evaluation_plan_version",
                self._plan.version,
            ),
            (
                "finding_fingerprints",
                self._serialize_json(
                    sorted(
                        finding.fingerprint
                        for finding
                        in normalized_findings
                    )
                ),
            ),
            (
                "relationship_counts",
                self._serialize_json(
                    {
                        relationship.value: (
                            relationship_counts[
                                relationship
                            ]
                        )
                        for relationship
                        in FindingRelationship
                    }
                ),
            ),
        )
        prototype = HypothesisEvaluation(
            id="pending",
            hypothesis_id=hypothesis_id,
            state=state,
            confidence=confidence,
            finding_refs=tuple(
                finding.id
                for finding in normalized_findings
            ),
            rationale=rationale,
            limitations=limitations,
            provenance=provenance,
        )
        evaluation_id = (
            self._build_evaluation_id(prototype)
        )

        return HypothesisEvaluation(
            id=evaluation_id,
            hypothesis_id=prototype.hypothesis_id,
            state=prototype.state,
            confidence=prototype.confidence,
            finding_refs=prototype.finding_refs,
            rationale=prototype.rationale,
            limitations=prototype.limitations,
            provenance=prototype.provenance,
        )

    def _select_state(
        self,
        *,
        finding_count: int,
        confidence: float,
        relationship_counts: dict[
            FindingRelationship,
            int,
        ],
    ) -> HypothesisEvaluationState:
        supporting_count = relationship_counts[
            FindingRelationship.SUPPORTING
        ]
        contradictory_count = relationship_counts[
            FindingRelationship.CONTRADICTORY
        ]
        decisive_sample = (
            finding_count
            >= self._plan.minimum_decisive_findings
        )

        if (
            decisive_sample
            and supporting_count == finding_count
            and confidence
            >= self._plan
            .supported_confidence_threshold
        ):
            return HypothesisEvaluationState.SUPPORTED

        if (
            decisive_sample
            and contradictory_count == finding_count
            and confidence
            >= self._plan
            .rejected_confidence_threshold
        ):
            return HypothesisEvaluationState.REJECTED

        if (
            supporting_count > 0
            and confidence
            >= self._plan
            .partially_supported_confidence_threshold
        ):
            return (
                HypothesisEvaluationState
                .PARTIALLY_SUPPORTED
            )

        return HypothesisEvaluationState.INCONCLUSIVE

    def _build_limitations(
        self,
        findings: tuple[Finding, ...],
        *,
        relationship_counts: dict[
            FindingRelationship,
            int,
        ],
    ) -> tuple[str, ...]:
        limitations = {
            limitation
            for finding in findings
            for limitation in finding.limitations
        }

        if (
            len(findings)
            < self._plan.minimum_decisive_findings
        ):
            limitations.add(
                f"only {len(findings)} findings available; "
                f"{self._plan.minimum_decisive_findings} "
                "required for a decisive state"
            )

        represented_relationships = sum(
            count > 0
            for count in relationship_counts.values()
        )

        if represented_relationships > 1:
            limitations.add(
                "findings have mixed relationships "
                "to the hypothesis"
            )

        if relationship_counts[
            FindingRelationship.INCONCLUSIVE
        ]:
            limitations.add(
                "one or more findings are inconclusive"
            )

        return tuple(sorted(limitations))

    @staticmethod
    def _normalize_findings(
        value: object,
    ) -> tuple[Finding, ...]:
        if not isinstance(value, tuple):
            raise TypeError(
                "findings must be a tuple"
            )

        if not value:
            raise ValueError(
                "findings must not be empty"
            )

        if any(
            not isinstance(finding, Finding)
            for finding in value
        ):
            raise TypeError(
                "each finding must be a Finding"
            )

        normalized = tuple(
            sorted(
                value,
                key=lambda finding: finding.id,
            )
        )
        finding_ids = tuple(
            finding.id
            for finding in normalized
        )

        if len(finding_ids) != len(set(finding_ids)):
            raise ValueError(
                "finding ids must be unique"
            )

        return normalized

    @staticmethod
    def _rationale_for_state(
        state: HypothesisEvaluationState,
    ) -> str:
        return {
            HypothesisEvaluationState.SUPPORTED: (
                "all findings support the hypothesis "
                "under the decisive plan rules"
            ),
            (
                HypothesisEvaluationState
                .PARTIALLY_SUPPORTED
            ): (
                "findings provide partial or mixed "
                "support under the plan rules"
            ),
            HypothesisEvaluationState.INCONCLUSIVE: (
                "available findings do not satisfy "
                "a decisive plan rule"
            ),
            HypothesisEvaluationState.REJECTED: (
                "all findings contradict the hypothesis "
                "under the decisive plan rules"
            ),
        }[state]

    @staticmethod
    def _serialize_json(
        value: object,
    ) -> str:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )

    @classmethod
    def _build_evaluation_id(
        cls,
        evaluation: HypothesisEvaluation,
    ) -> str:
        payload = evaluation.to_dict()
        del payload["id"]

        serialized = cls._serialize_json(payload)
        digest = sha256(
            serialized.encode("utf-8")
        ).hexdigest()

        return (
            "hypothesis-evaluation:sha256:"
            f"{digest}"
        )