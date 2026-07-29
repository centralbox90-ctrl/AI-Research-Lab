from src.application import public_api


EXPECTED_PUBLIC_NAMES = (
    "CompareStoredResearchArtifacts",
    "ExportStoredResearchArtifact",
    "GenerateResearchQuestionsFromKnowledgeRepositories",
    "GetExperimentExecutionHistory",
    "GetStoredResearchArtifact",
    "GetStoredResearchCycle",
    "IndicatorComparativeHypothesisEvaluationApplication",
    "KnowledgePromotionRejectedError",
    "KnowledgeResearchQuestionsResult",
    "ListStoredResearchCycles",
    "PromoteHypothesisEvaluationToKnowledge",
    "RunMarketResearch",
    "RunMarketResearchCampaign",
)

INTERNAL_NAMES = (
    "BuildKnowledgeGraphSnapshot",
    "ExperimentExecutionHistoryReader",
    "GenerateResearchQuestionsFromKnowledgeSnapshot",
    "KnowledgeGraphRelationRegistrar",
    "KnowledgeGraphSnapshotLoader",
    "MarketResearchSessionFactory",
    "ResearchArtifactSerializer",
    "SqliteKnowledgeRepository",
)


def test_exports_exact_public_use_case_surface(
) -> None:
    assert public_api.__all__ == (
        EXPECTED_PUBLIC_NAMES
    )

    for name in EXPECTED_PUBLIC_NAMES:
        exported = getattr(
            public_api,
            name,
        )

        assert exported.__module__.startswith(
            "src.application."
        )


def test_excludes_internal_components(
) -> None:
    for name in INTERNAL_NAMES:
        assert not hasattr(
            public_api,
            name,
        )
