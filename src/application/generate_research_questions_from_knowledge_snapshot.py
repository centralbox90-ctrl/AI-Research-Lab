from src.application.research_recommendation_question_adapter import (
    ResearchRecommendationQuestionAdapter,
)
from src.research.knowledge_gap_detector import (
    KnowledgeGapDetector,
)
from src.research.knowledge_graph_snapshot import (
    KnowledgeGraphSnapshot,
)
from src.research.question import ResearchQuestion
from src.research.research_recommendation_generator import (
    ResearchRecommendationGenerator,
)


class GenerateResearchQuestionsFromKnowledgeSnapshot:
    """
    Orchestrates deterministic knowledge-gap question generation.
    """

    def __init__(
        self,
        *,
        gap_detector: KnowledgeGapDetector,
        recommendation_generator: (
            ResearchRecommendationGenerator
        ),
        question_adapter: (
            ResearchRecommendationQuestionAdapter
        ),
    ) -> None:
        if not isinstance(
            gap_detector,
            KnowledgeGapDetector,
        ):
            raise TypeError(
                "gap_detector must be a "
                "KnowledgeGapDetector"
            )

        if not isinstance(
            recommendation_generator,
            ResearchRecommendationGenerator,
        ):
            raise TypeError(
                "recommendation_generator must be a "
                "ResearchRecommendationGenerator"
            )

        if not isinstance(
            question_adapter,
            ResearchRecommendationQuestionAdapter,
        ):
            raise TypeError(
                "question_adapter must be a "
                "ResearchRecommendationQuestionAdapter"
            )

        self._gap_detector = gap_detector
        self._recommendation_generator = (
            recommendation_generator
        )
        self._question_adapter = question_adapter

    def execute(
        self,
        snapshot: KnowledgeGraphSnapshot,
    ) -> tuple[ResearchQuestion, ...]:
        if not isinstance(
            snapshot,
            KnowledgeGraphSnapshot,
        ):
            raise TypeError(
                "snapshot must be a "
                "KnowledgeGraphSnapshot"
            )

        gaps = self._gap_detector.detect(
            snapshot
        )
        recommendations = (
            self._recommendation_generator
            .generate_all(gaps)
        )
        questions = tuple(
            self._question_adapter.adapt(
                recommendation
            )
            for recommendation
            in recommendations
        )
        question_ids = tuple(
            question.id
            for question in questions
        )

        if (
            len(question_ids)
            != len(set(question_ids))
        ):
            raise ValueError(
                "generated question IDs must be unique"
            )

        return questions
