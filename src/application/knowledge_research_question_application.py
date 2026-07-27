from datetime import datetime, timezone

from src.application.generate_research_questions_from_knowledge_snapshot import (
    GenerateResearchQuestionsFromKnowledgeSnapshot,
)
from src.application.research_recommendation_question_adapter import (
    ResearchQuestionClock,
    ResearchQuestionIdFactory,
    ResearchRecommendationQuestionAdapter,
)
from src.research.knowledge_gap_detector import (
    KnowledgeGapDetector,
)
from src.research.research_recommendation import (
    ResearchRecommendation,
)
from src.research.research_recommendation_generator import (
    ResearchRecommendationGenerator,
)


def system_utc_clock() -> datetime:
    """Return the current timezone-aware UTC time."""

    return datetime.now(timezone.utc)


def fingerprint_research_question_id(
    recommendation: ResearchRecommendation,
) -> str:
    """
    Derive a stable question ID from the recommendation fingerprint.
    """

    if not isinstance(
        recommendation,
        ResearchRecommendation,
    ):
        raise TypeError(
            "recommendation must be a "
            "ResearchRecommendation"
        )

    return (
        "knowledge-question-"
        + recommendation.fingerprint
    )


def build_knowledge_research_question_application(
    *,
    clock: ResearchQuestionClock = system_utc_clock,
    id_factory: ResearchQuestionIdFactory = (
        fingerprint_research_question_id
    ),
) -> GenerateResearchQuestionsFromKnowledgeSnapshot:
    """
    Build the knowledge research-question application graph.
    """

    return GenerateResearchQuestionsFromKnowledgeSnapshot(
        gap_detector=KnowledgeGapDetector(),
        recommendation_generator=(
            ResearchRecommendationGenerator()
        ),
        question_adapter=(
            ResearchRecommendationQuestionAdapter(
                clock=clock,
                id_factory=id_factory,
            )
        ),
    )
