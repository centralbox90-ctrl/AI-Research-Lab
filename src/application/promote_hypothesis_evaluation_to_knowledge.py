from __future__ import annotations

from src.application.knowledge_graph_relation_registrar import (
    KnowledgeGraphRelationRegistrar,
)
from src.application.ports.clock import Clock
from src.application.system_clock import SystemClock
from src.research.hypothesis_evaluation import (
    HypothesisEvaluation,
)
from src.research.knowledge_candidate import (
    KnowledgeCandidate,
)
from src.research.knowledge_candidate_validator import (
    KnowledgeCandidateValidator,
)
from src.research.knowledge_contradiction_detector import (
    KnowledgeContradictionDetector,
)
from src.research.knowledge_contradiction_rule import (
    KnowledgeContradictionRule,
)
from src.research.knowledge_promotion_policy import (
    KnowledgePromotionPolicy,
)
from src.research.knowledge_repository import (
    KnowledgeRepository,
)
from src.research.knowledge_revision import (
    KnowledgeRevision,
)


class KnowledgePromotionRejectedError(ValueError):
    """Raised when promotion policy rejects an evaluation."""

    def __init__(
        self,
        *,
        evaluation_id: str,
        reasons: tuple[str, ...],
    ) -> None:
        self.evaluation_id = evaluation_id
        self.reasons = reasons

        super().__init__(
            f"hypothesis evaluation {evaluation_id!r} "
            f"was not promoted: {'; '.join(reasons)}"
        )


class PromoteHypothesisEvaluationToKnowledge:
    """
    Promotes one allowed evaluation to an initial revision.
    """

    def __init__(
        self,
        *,
        promotion_policy: KnowledgePromotionPolicy,
        candidate_validator: (
            KnowledgeCandidateValidator
        ),
        knowledge_repository: KnowledgeRepository,
        contradiction_detector: (
            KnowledgeContradictionDetector
        ),
        contradiction_rules: tuple[
            KnowledgeContradictionRule,
            ...,
        ],
        relation_registrar: (
            KnowledgeGraphRelationRegistrar
        ),
        clock: Clock | None = None,
    ) -> None:
        if not isinstance(
            promotion_policy,
            KnowledgePromotionPolicy,
        ):
            raise TypeError(
                "promotion_policy must be a "
                "KnowledgePromotionPolicy"
            )

        if not isinstance(
            candidate_validator,
            KnowledgeCandidateValidator,
        ):
            raise TypeError(
                "candidate_validator must be a "
                "KnowledgeCandidateValidator"
            )

        if not isinstance(
            knowledge_repository,
            KnowledgeRepository,
        ):
            raise TypeError(
                "knowledge_repository must implement "
                "KnowledgeRepository"
            )

        if not isinstance(
            contradiction_detector,
            KnowledgeContradictionDetector,
        ):
            raise TypeError(
                "contradiction_detector must be a "
                "KnowledgeContradictionDetector"
            )

        if not isinstance(
            contradiction_rules,
            tuple,
        ):
            raise TypeError(
                "contradiction_rules must be a tuple"
            )

        if any(
            not isinstance(
                rule,
                KnowledgeContradictionRule,
            )
            for rule in contradiction_rules
        ):
            raise TypeError(
                "contradiction_rules must contain only "
                "KnowledgeContradictionRule values"
            )

        if not isinstance(
            relation_registrar,
            KnowledgeGraphRelationRegistrar,
        ):
            raise TypeError(
                "relation_registrar must be a "
                "KnowledgeGraphRelationRegistrar"
            )

        resolved_clock = clock or SystemClock()

        if not callable(
            getattr(
                resolved_clock,
                "now",
                None,
            )
        ):
            raise TypeError(
                "clock must provide a callable now method"
            )

        self._promotion_policy = promotion_policy
        self._candidate_validator = (
            candidate_validator
        )
        self._knowledge_repository = (
            knowledge_repository
        )
        self._contradiction_detector = (
            contradiction_detector
        )
        self._contradiction_rules = (
            contradiction_rules
        )
        self._relation_registrar = (
            relation_registrar
        )
        self._clock = resolved_clock

    def run(
        self,
        *,
        evaluation: HypothesisEvaluation,
        knowledge_id: str,
        statement: str,
        applicability: tuple[str, ...],
        limitations: tuple[str, ...],
        provenance: tuple[
            tuple[str, str],
            ...,
        ],
    ) -> KnowledgeRevision:
        reasons = (
            self._promotion_policy
            .rejection_reasons(
                evaluation=evaluation,
            )
        )

        if reasons:
            raise KnowledgePromotionRejectedError(
                evaluation_id=evaluation.id,
                reasons=reasons,
            )

        candidate = KnowledgeCandidate(
            id=knowledge_id,
            statement=statement,
            confidence=evaluation.confidence,
            applicability=applicability,
            limitations=limitations,
            supporting_findings=(
                evaluation.finding_refs
            ),
            hypothesis_evaluation_ref=(
                evaluation.id
            ),
            provenance=provenance,
        )

        authoritative_provenance = dict(
            candidate.provenance
        )
        authoritative_provenance.update(
            {
                "hypothesis_evaluation_fingerprint": (
                    evaluation.fingerprint
                ),
                "hypothesis_evaluation_state": (
                    evaluation.state.value
                ),
                "hypothesis_id": (
                    evaluation.hypothesis_id
                ),
                "knowledge_promotion_allowed_states": (
                    ",".join(
                        state.value
                        for state
                        in (
                            self
                            ._promotion_policy
                            .allowed_states
                        )
                    )
                ),
                "knowledge_promotion_minimum_confidence": (
                    repr(
                        self
                        ._promotion_policy
                        .minimum_confidence
                    )
                ),
                "knowledge_promotion_minimum_findings": (
                    str(
                        self
                        ._promotion_policy
                        .minimum_findings
                    )
                ),
                "knowledge_promotion_policy_version": (
                    "1"
                ),
            }
        )

        candidate = KnowledgeCandidate(
            id=candidate.id,
            statement=candidate.statement,
            confidence=candidate.confidence,
            applicability=candidate.applicability,
            limitations=candidate.limitations,
            supporting_findings=(
                candidate.supporting_findings
            ),
            hypothesis_evaluation_ref=(
                candidate.hypothesis_evaluation_ref
            ),
            provenance=tuple(
                authoritative_provenance.items()
            ),
        )

        item = self._candidate_validator.validate(
            candidate=candidate,
        )
        revision = KnowledgeRevision(
            item=item,
            valid_from=self._clock.now(),
            change_reason=(
                "Promoted from hypothesis evaluation "
                f"{evaluation.id}"
            ),
            supersedes_version=None,
        )

        self._knowledge_repository.save(
            revision
        )

        contradictions = (
            self._contradiction_detector.detect(
                repository=(
                    self._knowledge_repository
                ),
                rules=self._contradiction_rules,
            )
        )

        for contradiction in contradictions:
            references_promoted_item = any(
                item.fingerprint
                == revision.item.fingerprint
                for item in contradiction.items
            )

            if not references_promoted_item:
                continue

            self._knowledge_repository.save_contradiction(
                contradiction
            )
            self._relation_registrar.register_contradiction(
                contradiction
            )

        return revision
