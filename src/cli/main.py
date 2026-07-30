import argparse
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import TextIO

from src.application import (
    ExportStoredResearchArtifact,
    GetStoredResearchArtifact,
    GetStoredResearchCycle,
    ListStoredResearchCycles,
)
from src.application.get_experiment_execution_history import (
    GetExperimentExecutionHistory,
)
from src.application.list_experiment_executions import (
    ListExperimentExecutions,
)
from src.application.artifact_comparison_input_extractor import (
    ArtifactComparisonInputExtractor,
)
from src.application.build_knowledge_graph_snapshot import (
    BuildKnowledgeGraphSnapshot,
)
from src.application.knowledge_graph_relation_registrar import (
    KnowledgeGraphRelationRegistrar,
)
from src.application.compare_stored_research_artifacts import (
    CompareStoredResearchArtifacts,
)
from src.application.canonical_market_data_provider import (
    CanonicalMarketDataProvider,
)
from src.application.generated_market_data_provider import (
    GeneratedMarketDataProvider,
)
from src.application.git_code_version_provider import (
    GitCodeVersionProvider,
)
from src.application.git_command_runner import (
    GitCommandRunner,
)
from src.application.hypothesis_evaluation_artifact_envelope_factory import (
    HypothesisEvaluationArtifactEnvelopeFactory,
)
from src.application.knowledge_research_questions_artifact_envelope_factory import (
    KnowledgeResearchQuestionsArtifactEnvelopeFactory,
)
from src.application.research_artifact_envelope import (
    ResearchArtifactEnvelopeFactory,
)
from src.application.generate_research_questions_from_knowledge_repositories import (
    GenerateResearchQuestionsFromKnowledgeRepositories,
)
from src.application.knowledge_research_question_application import (
    build_knowledge_research_question_application,
)
from src.application.market_research_application import (
    build_market_research_application,
)
from src.application.market_research_campaign_artifact_envelope_factory import (
    MarketResearchCampaignArtifactEnvelopeFactory,
)
from src.application.promote_hypothesis_evaluation_to_knowledge import (
    PromoteHypothesisEvaluationToKnowledge,
)
from src.application.simple_market_signal_provider import (
    SimpleMarketSignalProvider,
)
from src.cli.compare_research_artifacts_command import (
    CompareResearchArtifactsCommand,
)
from src.cli.export_research_artifact_command import (
    ExportResearchArtifactCommand,
)
from src.cli.generate_research_questions_from_knowledge_repositories_command import (
    GenerateResearchQuestionsFromKnowledgeRepositoriesCommand,
)
from src.cli.get_experiment_execution_history_command import (
    GetExperimentExecutionHistoryCommand,
)
from src.cli.get_stored_research_artifact_command import (
    GetStoredResearchArtifactCommand,
)
from src.cli.get_stored_research_cycle_command import (
    GetStoredResearchCycleCommand,
)
from src.cli.list_experiment_executions_command import (
    ListExperimentExecutionsCommand,
)
from src.cli.list_stored_research_cycles_command import (
    ListStoredResearchCyclesCommand,
)
from src.cli.indicator_comparative_hypothesis_evaluation_composition_root import (
    build_default_indicator_comparative_hypothesis_evaluation_command,
)
from src.cli.research_cli import ResearchCli
from src.cli.run_market_research_campaign_command import (
    RunMarketResearchCampaignCommand,
)
from src.cli.run_market_research_command import (
    RunMarketResearchCommand,
)
from src.research.hypothesis_evaluation import (
    HypothesisEvaluationState,
)
from src.research.knowledge_candidate_validator import (
    KnowledgeCandidateValidator,
)
from src.research.knowledge_contradiction_detector import (
    KnowledgeContradictionDetector,
)
from src.research.knowledge_promotion_policy import (
    KnowledgePromotionPolicy,
)
from src.storage import (
    RESEARCH_CYCLE_DATABASE_PATH,
    SqliteExperimentExecutionRecorder,
    SqliteKnowledgeRelationRepository,
    SqliteKnowledgeRepository,
    SqliteResearchCycleStore,
)


def build_research_cli(
    db_path: str | Path = RESEARCH_CYCLE_DATABASE_PATH,
) -> ResearchCli:
    """
    Build the persistent AI Research Lab CLI dependency graph.

    All commands share one SQLite research-cycle store.
    """

    store = SqliteResearchCycleStore(
        db_path=db_path,
    )

    execution_recorder = (
        SqliteExperimentExecutionRecorder(
            db_path=db_path,
        )
    )

    execution_history_application = (
        GetExperimentExecutionHistory(
            reader=execution_recorder,
        )
    )

    execution_history_command = (
        GetExperimentExecutionHistoryCommand(
            application=(
                execution_history_application
            ),
        )
    )

    execution_listing_application = (
        ListExperimentExecutions(
            catalog=execution_recorder,
        )
    )

    execution_listing_command = (
        ListExperimentExecutionsCommand(
            application=(
                execution_listing_application
            ),
        )
    )

    get_stored_cycle = GetStoredResearchCycle(
        store=store,
    )

    get_cycle_command = GetStoredResearchCycleCommand(
        get_stored_research_cycle=get_stored_cycle,
    )

    get_stored_artifact = GetStoredResearchArtifact(
        store=store,
    )

    get_artifact_command = (
        GetStoredResearchArtifactCommand(
            get_stored_research_artifact=get_stored_artifact,
        )
    )

    export_stored_artifact = ExportStoredResearchArtifact(
        get_stored_research_artifact=get_stored_artifact,
    )

    export_artifact_command = ExportResearchArtifactCommand(
        export_stored_research_artifact=(
            export_stored_artifact
        ),
    )

    compare_stored_artifacts = CompareStoredResearchArtifacts(
        artifact_getter=get_stored_artifact,
        input_extractor=ArtifactComparisonInputExtractor(),
    )

    compare_artifacts_command = CompareResearchArtifactsCommand(
        compare_stored_research_artifacts=(
            compare_stored_artifacts
        ),
    )

    list_stored_cycles = ListStoredResearchCycles(
        store=store,
    )

    list_command = ListStoredResearchCyclesCommand(
        list_stored_research_cycles=list_stored_cycles,
    )

    market_research_application = (
        build_market_research_application(
            data_provider=GeneratedMarketDataProvider(),
            signal_provider=SimpleMarketSignalProvider(),
            store=store,
            execution_recorder=execution_recorder,
        )
    )

    run_command = RunMarketResearchCommand(
        run_market_research=market_research_application,
    )

    knowledge_repository = SqliteKnowledgeRepository(
        db_path=db_path,
    )

    knowledge_relation_repository = (
        SqliteKnowledgeRelationRepository(
            db_path=db_path,
            knowledge_repository=(
                knowledge_repository
            ),
        )
    )

    promotion_application = (
        PromoteHypothesisEvaluationToKnowledge(
            promotion_policy=(
                KnowledgePromotionPolicy(
                    allowed_states=(
                        HypothesisEvaluationState.SUPPORTED,
                    ),
                    minimum_confidence=0.75,
                    minimum_findings=2,
                )
            ),
            candidate_validator=(
                KnowledgeCandidateValidator(
                    minimum_confidence=0.75,
                    minimum_supporting_findings=2,
                )
            ),
            knowledge_repository=(
                knowledge_repository
            ),
            contradiction_detector=(
                KnowledgeContradictionDetector()
            ),
            contradiction_rules=(),
            relation_registrar=(
                KnowledgeGraphRelationRegistrar(
                    knowledge_repository=(
                        knowledge_repository
                    ),
                    relation_repository=(
                        knowledge_relation_repository
                    ),
                )
            ),
        )
    )

    knowledge_snapshot_builder = (
        BuildKnowledgeGraphSnapshot(
            knowledge_repository=(
                knowledge_repository
            ),
            relation_repository=(
                knowledge_relation_repository
            ),
        )
    )

    knowledge_question_application = (
        GenerateResearchQuestionsFromKnowledgeRepositories(
            snapshot_builder=(
                knowledge_snapshot_builder
            ),
            question_generator=(
                build_knowledge_research_question_application()
            ),
        )
    )

    application_code_version = (
        GitCodeVersionProvider(
            git_commit_reader=GitCommandRunner(),
            fallback="development",
        ).get_code_version()
    )

    campaign_envelope_factory = (
        MarketResearchCampaignArtifactEnvelopeFactory(
            envelope_factory=(
                ResearchArtifactEnvelopeFactory(
                    producer=(
                        "market-research-campaign"
                    ),
                    producer_version=(
                        application_code_version
                    ),
                )
            )
        )
    )

    run_campaign_command = RunMarketResearchCampaignCommand(
        runner=market_research_application,
        artifact_envelope_factory=(
            campaign_envelope_factory
        ),
    )
    knowledge_question_envelope_factory = (
        KnowledgeResearchQuestionsArtifactEnvelopeFactory(
            envelope_factory=(
                ResearchArtifactEnvelopeFactory(
                    producer=(
                        "knowledge-question-generator"
                    ),
                    producer_version=(
                        application_code_version
                    ),
                )
            )
        )
    )

    knowledge_question_command = (
        GenerateResearchQuestionsFromKnowledgeRepositoriesCommand(
            application=(
                knowledge_question_application
            ),
            artifact_envelope_factory=(
                knowledge_question_envelope_factory
            ),
        )
    )

    hypothesis_evaluation_envelope_factory = (
        HypothesisEvaluationArtifactEnvelopeFactory(
            envelope_factory=(
                ResearchArtifactEnvelopeFactory(
                    producer=(
                        "comparative-hypothesis-evaluation"
                    ),
                    producer_version=(
                        application_code_version
                    ),
                )
            )
        )
    )

    comparative_evaluation_command = (
        build_default_indicator_comparative_hypothesis_evaluation_command(
            data_provider=CanonicalMarketDataProvider(
                GeneratedMarketDataProvider()
            ),
            execution_recorder=execution_recorder,
            code_version=application_code_version,
            promotion_application=(
                promotion_application
            ),
            artifact_envelope_factory=(
                hypothesis_evaluation_envelope_factory
            ),
        )
    )

    return ResearchCli(
        get_research_cycle_command=get_cycle_command,
        get_research_artifact_command=get_artifact_command,
        export_research_artifact_command=(
            export_artifact_command
        ),
        compare_research_artifacts_command=(
            compare_artifacts_command
        ),
        list_research_cycles_command=list_command,
        list_experiment_executions_command=(
            execution_listing_command
        ),
        get_experiment_execution_history_command=(
            execution_history_command
        ),
        run_research_command=run_command,
        generate_research_questions_command=(
            knowledge_question_command
        ),
        run_market_research_campaign_command=(
            run_campaign_command
        ),
        run_comparative_hypothesis_evaluation_command=(
            comparative_evaluation_command
        ),
    )


def main(
    argv: Sequence[str] | None = None,
    *,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    """
    Run the AI Research Lab persistent CLI process.

    A custom database path may be supplied explicitly.
    """

    output_stream = stdout or sys.stdout
    error_stream = stderr or sys.stderr

    parser = argparse.ArgumentParser(
        prog="ai-research-lab",
        description=(
            "AI Research Lab persistent command-line interface."
        ),
        add_help=False,
    )

    parser.add_argument(
        "--database",
        default=str(RESEARCH_CYCLE_DATABASE_PATH),
        help=(
            "Path to the SQLite research-cycle database. "
            "Defaults to .research_lab/research_cycles.db."
        ),
    )

    try:
        arguments, remaining_arguments = parser.parse_known_args(
            argv,
        )
    except SystemExit as error:
        return int(error.code)

    cli = build_research_cli(
        db_path=arguments.database,
    )

    return cli.run(
        remaining_arguments,
        stdout=output_stream,
        stderr=error_stream,
    )


if __name__ == "__main__":
    raise SystemExit(main())