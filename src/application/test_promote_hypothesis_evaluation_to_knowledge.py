from __future__ import annotations

from datetime import UTC, datetime

import pytest

from src.application.in_memory_knowledge_relation_repository import (
    InMemoryKnowledgeRelationRepository,
)
from src.application.knowledge_graph_relation_registrar import (
    KnowledgeGraphRelationRegistrar,
)
from src.application.promote_hypothesis_evaluation_to_knowledge import (
    KnowledgePromotionRejectedError,
    PromoteHypothesisEvaluationToKnowledge,
)
from src.research.hypothesis_evaluation import (
    HypothesisEvaluation,
    HypothesisEvaluationState,
)
from src.research.knowledge_applicability_query import (
    KnowledgeApplicabilityQuery,
)
from src.research.knowledge_candidate_validator import (
    KnowledgeCandidateValidationError,
    KnowledgeCandidateValidator,
)
from src.research.knowledge_contradiction_detector import (
    KnowledgeContradictionDetector,
)
from src.research.knowledge_contradiction_rule import (
    KnowledgeContradictionRule,
)
from src.research.knowledge_contradiction import (
    KnowledgeContradiction,
)
from src.research.knowledge_item import (
    KnowledgeItem,
)
from src.research.knowledge_promotion_policy import (
    KnowledgePromotionPolicy,
)
from src.research.knowledge_relation import (
    KnowledgeRelationType,
)
from src.research.knowledge_revision import (
    KnowledgeRevision,
)


class FixedClock:
    def __init__(
        self,
        value: datetime,
    ) -> None:
        self.value = value

    def now(self) -> datetime:
        return self.value


class RecordingKnowledgeRepository:
    def __init__(self) -> None:
        self.revisions: list[
            KnowledgeRevision
        ] = []
        self.contradictions: list[
            KnowledgeContradiction
        ] = []

    def save(
        self,
        revision: KnowledgeRevision,
    ) -> None:
        self.revisions.append(revision)

    def get(
        self,
        item_id: str,
    ) -> KnowledgeItem | None:
        matching = tuple(
            revision.item
            for revision in self.revisions
            if revision.item.id == item_id
        )

        if not matching:
            return None

        return matching[-1]

    def get_version(
        self,
        item_id: str,
        version: int,
    ) -> KnowledgeRevision | None:
        for revision in self.revisions:
            if (
                revision.item.id == item_id
                and revision.item.version == version
            ):
                return revision

        return None

    def history(
        self,
        item_id: str,
    ) -> tuple[KnowledgeRevision, ...]:
        return tuple(
            revision
            for revision in self.revisions
            if revision.item.id == item_id
        )

    def list_all(
        self,
    ) -> tuple[KnowledgeItem, ...]:
        latest: dict[str, KnowledgeItem] = {}

        for revision in self.revisions:
            latest[revision.item.id] = (
                revision.item
            )

        return tuple(
            latest[item_id]
            for item_id in sorted(latest)
        )

    def find_applicable(
        self,
        query: KnowledgeApplicabilityQuery,
    ) -> tuple[KnowledgeItem, ...]:
        return tuple(
            item
            for item in self.list_all()
            if query.matches(item)
        )

    def save_contradiction(
        self,
        contradiction: KnowledgeContradiction,
    ) -> None:
        self.contradictions.append(
            contradiction
        )

    def list_contradictions(
        self,
    ) -> tuple[KnowledgeContradiction, ...]:
        return tuple(self.contradictions)

    def contradictions_for(
        self,
        item_id: str,
    ) -> tuple[KnowledgeContradiction, ...]:
        return tuple(
            contradiction
            for contradiction
            in self.contradictions
            if any(
                item.id == item_id
                for item
                in contradiction.items
            )
        )


def _evaluation(
    *,
    state: HypothesisEvaluationState = (
        HypothesisEvaluationState.SUPPORTED
    ),
    confidence: float = 0.85,
    finding_refs: tuple[str, ...] = (
        "finding-1",
        "finding-2",
    ),
) -> HypothesisEvaluation:
    return HypothesisEvaluation(
        id="evaluation-1",
        hypothesis_id="hypothesis-1",
        state=state,
        confidence=confidence,
        finding_refs=finding_refs,
        rationale=("consistent supporting findings",),
        provenance=(("producer", "test"),),
    )


def _policy(
    *,
    minimum_confidence: float = 0.75,
    minimum_findings: int = 2,
) -> KnowledgePromotionPolicy:
    return KnowledgePromotionPolicy(
        allowed_states=(
            HypothesisEvaluationState.SUPPORTED,
        ),
        minimum_confidence=minimum_confidence,
        minimum_findings=minimum_findings,
    )


def _application(
    *,
    repository: RecordingKnowledgeRepository,
    policy: KnowledgePromotionPolicy | None = None,
    relation_repository: (
        InMemoryKnowledgeRelationRepository
        | None
    ) = None,
    contradiction_rules: tuple[
        KnowledgeContradictionRule,
        ...,
    ] = (),
) -> PromoteHypothesisEvaluationToKnowledge:
    resolved_relation_repository = (
        relation_repository
        or InMemoryKnowledgeRelationRepository(
            repository
        )
    )

    return PromoteHypothesisEvaluationToKnowledge(
        promotion_policy=policy or _policy(),
        candidate_validator=(
            KnowledgeCandidateValidator(
                minimum_confidence=0.75,
                minimum_supporting_findings=2,
            )
        ),
        knowledge_repository=repository,
        contradiction_detector=(
            KnowledgeContradictionDetector()
        ),
        contradiction_rules=contradiction_rules,
        relation_registrar=(
            KnowledgeGraphRelationRegistrar(
                knowledge_repository=repository,
                relation_repository=(
                    resolved_relation_repository
                ),
            )
        ),
        clock=FixedClock(
            datetime(
                2026,
                7,
                28,
                12,
                0,
                tzinfo=UTC,
            )
        ),
    )


def _run(
    application: (
        PromoteHypothesisEvaluationToKnowledge
    ),
    *,
    evaluation: HypothesisEvaluation,
) -> KnowledgeRevision:
    return application.run(
        evaluation=evaluation,
        knowledge_id="knowledge-1",
        statement=(
            "Momentum persists in liquid markets."
        ),
        applicability=(
            "liquid markets",
            "trend regimes",
        ),
        limitations=(
            "crisis regimes not evaluated",
        ),
        provenance=(
            ("dataset_fingerprint", "dataset-1"),
        ),
    )


def test_promotes_and_stores_initial_revision():
    repository = RecordingKnowledgeRepository()
    evaluation = _evaluation()

    revision = _run(
        _application(repository=repository),
        evaluation=evaluation,
    )

    assert repository.revisions == [revision]
    assert revision.item.id == "knowledge-1"
    assert revision.item.version == 1
    assert revision.item.confidence == 0.85
    assert revision.item.supporting_findings == (
        "finding-1",
        "finding-2",
    )
    assert revision.valid_from == datetime(
        2026,
        7,
        28,
        12,
        0,
        tzinfo=UTC,
    )
    assert revision.change_reason == (
        "Promoted from hypothesis evaluation "
        "evaluation-1"
    )
    assert revision.supersedes_version is None

    provenance = dict(
        revision.item.provenance
    )

    assert provenance[
        "hypothesis_evaluation_fingerprint"
    ] == evaluation.fingerprint
    assert provenance[
        "hypothesis_evaluation_state"
    ] == "supported"
    assert provenance["hypothesis_id"] == (
        "hypothesis-1"
    )
    assert provenance[
        "knowledge_promotion_policy_version"
    ] == "1"


def test_policy_rejection_prevents_storage():
    repository = RecordingKnowledgeRepository()
    evaluation = _evaluation(
        state=(
            HypothesisEvaluationState
            .PARTIALLY_SUPPORTED
        ),
    )

    with pytest.raises(
        KnowledgePromotionRejectedError
    ) as error:
        _run(
            _application(repository=repository),
            evaluation=evaluation,
        )

    assert error.value.evaluation_id == (
        "evaluation-1"
    )
    assert error.value.reasons == (
        "state must be one of: supported",
    )
    assert repository.revisions == []


def test_candidate_validation_prevents_storage():
    repository = RecordingKnowledgeRepository()
    evaluation = _evaluation(
        confidence=0.6,
        finding_refs=("finding-1",),
    )
    application = _application(
        repository=repository,
        policy=_policy(
            minimum_confidence=0.5,
            minimum_findings=1,
        ),
    )

    with pytest.raises(
        KnowledgeCandidateValidationError
    ):
        _run(
            application,
            evaluation=evaluation,
        )

    assert repository.revisions == []


def test_stores_and_projects_detected_contradiction():
    repository = RecordingKnowledgeRepository()
    existing_item = KnowledgeItem(
        id="knowledge-0",
        statement=(
            "Momentum does not persist in liquid markets."
        ),
        confidence=0.9,
        applicability=("liquid markets",),
        limitations=("single market family",),
        supporting_findings=(
            "existing-finding-1",
            "existing-finding-2",
        ),
        version=1,
        provenance=(("producer", "existing-test"),),
    )
    repository.save(
        KnowledgeRevision(
            item=existing_item,
            valid_from=datetime(
                2026,
                7,
                28,
                11,
                0,
                tzinfo=UTC,
            ),
            change_reason="Existing knowledge.",
            supersedes_version=None,
        )
    )
    relation_repository = (
        InMemoryKnowledgeRelationRepository(
            repository
        )
    )
    contradiction_rule = (
        KnowledgeContradictionRule(
            statements=(
                existing_item.statement,
                (
                    "Momentum persists in "
                    "liquid markets."
                ),
            ),
            reason=(
                "Opposing conclusions for "
                "the same applicability."
            ),
        )
    )

    revision = _run(
        _application(
            repository=repository,
            relation_repository=(
                relation_repository
            ),
            contradiction_rules=(
                contradiction_rule,
            ),
        ),
        evaluation=_evaluation(),
    )

    contradictions = (
        repository.list_contradictions()
    )
    relations = relation_repository.list_all()

    assert len(contradictions) == 1
    assert revision.item in (
        contradictions[0].items
    )
    assert len(relations) == 1
    assert (
        relations[0].relation_type
        is KnowledgeRelationType.CONTRADICTS
    )
    assert relations[0].reason == (
        "Opposing conclusions for "
        "the same applicability."
    )
