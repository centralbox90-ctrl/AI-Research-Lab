from src.research.knowledge_gap import (
    KnowledgeGap,
    KnowledgeGapType,
)
from src.research.research_recommendation import (
    ResearchRecommendation,
    ResearchRecommendationPriority,
)


_PRIORITY_ORDER = {
    ResearchRecommendationPriority.HIGH: 0,
    ResearchRecommendationPriority.MEDIUM: 1,
    ResearchRecommendationPriority.LOW: 2,
}


def _normalize_gap(
    value: object,
) -> KnowledgeGap:
    if not isinstance(value, KnowledgeGap):
        raise TypeError(
            "gap must be a KnowledgeGap"
        )

    return value


def _recommendation_key(
    recommendation: ResearchRecommendation,
) -> tuple[object, ...]:
    return (
        _PRIORITY_ORDER[
            recommendation.priority
        ],
        recommendation.question,
        recommendation.fingerprint,
    )


class ResearchRecommendationGenerator:
    """
    Generates deterministic research recommendations from gaps.
    """

    def generate(
        self,
        gap: KnowledgeGap,
    ) -> ResearchRecommendation:
        normalized_gap = _normalize_gap(gap)

        if (
            normalized_gap.gap_type
            is KnowledgeGapType.ISOLATED_ITEM
        ):
            item = normalized_gap.items[0]
            priority = (
                ResearchRecommendationPriority.LOW
            )
            question = (
                f'How can "{item.statement}" '
                "be connected to existing "
                "knowledge?"
            )
            rationale = (
                "The knowledge item has no "
                "graph relations in the "
                "referenced snapshot."
            )
        elif (
            normalized_gap.gap_type
            is KnowledgeGapType.UNSUPPORTED_ITEM
        ):
            item = normalized_gap.items[0]
            priority = (
                ResearchRecommendationPriority
                .MEDIUM
            )
            question = (
                "What independent evidence "
                f'supports "{item.statement}"?'
            )
            rationale = (
                "The knowledge item lacks "
                "active incoming supports and "
                "outgoing derived_from "
                "relations."
            )
        else:
            left, right = normalized_gap.items
            priority = (
                ResearchRecommendationPriority
                .HIGH
            )
            question = (
                "Under which conditions can "
                f'"{left.statement}" and '
                f'"{right.statement}" be '
                "reconciled?"
            )
            rationale = (
                "The active knowledge items "
                "contradict each other within "
                "overlapping applicability."
            )

        return ResearchRecommendation(
            gap=normalized_gap,
            priority=priority,
            question=question,
            rationale=rationale,
        )

    def generate_all(
        self,
        gaps: tuple[KnowledgeGap, ...],
    ) -> tuple[
        ResearchRecommendation,
        ...,
    ]:
        if not isinstance(gaps, tuple):
            raise TypeError(
                "gaps must be a tuple"
            )

        recommendations: dict[
            str,
            ResearchRecommendation,
        ] = {}

        for gap in gaps:
            if not isinstance(
                gap,
                KnowledgeGap,
            ):
                raise TypeError(
                    "each gap must be a "
                    "KnowledgeGap"
                )

            recommendation = self.generate(
                gap
            )
            recommendations.setdefault(
                recommendation.fingerprint,
                recommendation,
            )

        return tuple(
            sorted(
                recommendations.values(),
                key=_recommendation_key,
            )
        )
