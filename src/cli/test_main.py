import json
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path

from src.application.promote_hypothesis_evaluation_to_knowledge import (
    PromoteHypothesisEvaluationToKnowledge,
)
from src.cli import (
    build_research_cli,
    main,
)
from src.cli.generate_research_questions_from_knowledge_repositories_command import (
    GenerateResearchQuestionsFromKnowledgeRepositoriesCommand,
)
from src.cli.run_indicator_comparative_hypothesis_evaluation_command import (
    RunIndicatorComparativeHypothesisEvaluationCommand,
)
from src.cli.run_market_research_campaign_command import (
    RunMarketResearchCampaignCommand,
)
from src.research.hypothesis_evaluation import (
    HypothesisEvaluation,
    HypothesisEvaluationState,
)
from src.research.knowledge_item import KnowledgeItem
from src.research.knowledge_revision import (
    KnowledgeRevision,
)
from src.storage import (
    SqliteKnowledgeRepository,
    SqliteResearchCycleStore,
)


def test_main_reads_research_cycle_from_sqlite_database(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "research_cycles.db"

    store = SqliteResearchCycleStore(
        db_path=db_path,
    )

    store.save(
        result_id="result-001",
        serialized_cycle={
            "result": {
                "id": "result-001",
                "success": True,
            },
            "evidence_strength_evaluation": {
                "level": "very_strong",
            },
            "hypothesis_decision": {
                "is_supported": True,
            },
            "next_experiment_selection": {
                "action": "replicate_experiment",
            },
        },
    )

    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        [
            "--database",
            str(db_path),
            "get-research-cycle",
            "result-001",
        ],
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 0
    assert stderr.getvalue() == ""

    parsed = json.loads(stdout.getvalue())

    assert parsed["result"]["id"] == "result-001"
    assert parsed["result"]["success"] is True

    assert (
        parsed["evidence_strength_evaluation"]["level"]
        == "very_strong"
    )

    assert parsed["hypothesis_decision"]["is_supported"] is True

    assert (
        parsed["next_experiment_selection"]["action"]
        == "replicate_experiment"
    )


def test_main_reports_missing_research_cycle(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "research_cycles.db"

    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        [
            "--database",
            str(db_path),
            "get-research-cycle",
            "unknown-result-id",
        ],
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 1
    assert stdout.getvalue() == ""
    assert (
        stderr.getvalue()
        == "Research cycle not found: unknown-result-id\n"
    )


def test_build_research_cli_configures_comparative_command(
    tmp_path: Path,
) -> None:
    cli = build_research_cli(
        db_path=tmp_path / "research_cycles.db",
    )

    command = (
        cli.run_comparative_hypothesis_evaluation_command
    )

    assert isinstance(
        command,
        RunIndicatorComparativeHypothesisEvaluationCommand,
    )
    assert isinstance(
        command._promotion_application,
        PromoteHypothesisEvaluationToKnowledge,
    )
    assert (
        command
        ._promotion_application
        ._knowledge_repository
        is
        cli.generate_research_questions_command
        ._snapshot_builder
        ._knowledge_repository
    )


def test_build_research_cli_configures_campaign_command(
    tmp_path: Path,
) -> None:
    cli = build_research_cli(
        db_path=tmp_path / "research_cycles.db",
    )

    assert isinstance(
        cli.run_market_research_campaign_command,
        RunMarketResearchCampaignCommand,
    )


def test_build_research_cli_configures_knowledge_command(
    tmp_path: Path,
) -> None:
    cli = build_research_cli(
        db_path=tmp_path / "research_cycles.db",
    )

    assert isinstance(
        cli.generate_research_questions_command,
        GenerateResearchQuestionsFromKnowledgeRepositoriesCommand,
    )


def test_main_generates_questions_from_stored_knowledge(
    tmp_path: Path,
) -> None:
    db_path = (
        tmp_path / "research-cycles.db"
    )
    knowledge_repository = (
        SqliteKnowledgeRepository(
            db_path=db_path,
        )
    )
    item = KnowledgeItem(
        id="knowledge-1",
        statement="Momentum persists.",
        confidence=0.85,
        applicability=("liquid markets",),
        limitations=("limited history",),
        supporting_findings=(
            "finding-1",
            "finding-2",
        ),
        version=1,
        provenance=(("producer", "test"),),
    )
    knowledge_repository.save(
        KnowledgeRevision(
            item=item,
            valid_from=datetime(
                2026,
                7,
                28,
                12,
                0,
                tzinfo=timezone.utc,
            ),
            change_reason="Initial knowledge.",
            supersedes_version=None,
        )
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        [
            "--database",
            str(db_path),
            "generate-knowledge-research-questions",
            "--compact",
        ],
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 0
    assert stderr.getvalue() == ""

    payload = json.loads(stdout.getvalue())

    assert payload["artifact_type"] == (
        "knowledge_research_questions"
    )
    assert payload["artifact_version"] == 1
    assert payload["question_count"] == 1
    assert len(payload["questions"]) == 1
    assert len(
        payload["snapshot_fingerprint"]
    ) == 64

def test_promoted_evaluation_generates_questions_from_shared_repository(
    tmp_path: Path,
) -> None:
    cli = build_research_cli(
        db_path=tmp_path / "research-cycles.db",
    )
    evaluation = HypothesisEvaluation(
        id=(
            "hypothesis-evaluation:"
            "sha256:production-vertical-path"
        ),
        hypothesis_id="hypothesis-rsi",
        state=HypothesisEvaluationState.SUPPORTED,
        confidence=0.82,
        finding_refs=(
            "finding-a",
            "finding-b",
        ),
        rationale=(
            "Replicated findings support the hypothesis.",
        ),
        limitations=(),
        provenance=(
            (
                "evaluation_plan_version",
                "hypothesis-evaluation-v1",
            ),
        ),
    )

    revision = (
        cli
        .run_comparative_hypothesis_evaluation_command
        ._promotion_application
        .run(
            evaluation=evaluation,
            knowledge_id="knowledge-rsi",
            statement=(
                "RSI effect persists across markets."
            ),
            applicability=("liquid FX",),
            limitations=("generated data",),
            provenance=(
                ("producer", "production-test"),
            ),
        )
    )

    rendered = (
        cli
        .generate_research_questions_command
        .execute(indent=None)
    )
    payload = json.loads(rendered)

    assert revision.item.id == "knowledge-rsi"
    assert revision.item.version == 1
    assert payload["artifact_type"] == (
        "knowledge_research_questions"
    )
    assert payload["question_count"] == 1
    assert len(payload["questions"]) == 1
    assert len(
        payload["snapshot_fingerprint"]
    ) == 64


def test_promoted_evaluation_generates_questions_from_shared_repository(
    tmp_path: Path,
) -> None:
    cli = build_research_cli(
        db_path=tmp_path / "research-cycles.db",
    )
    evaluation = HypothesisEvaluation(
        id=(
            "hypothesis-evaluation:"
            "sha256:production-vertical-path"
        ),
        hypothesis_id="hypothesis-rsi",
        state=HypothesisEvaluationState.SUPPORTED,
        confidence=0.82,
        finding_refs=(
            "finding-a",
            "finding-b",
        ),
        rationale=(
            "Replicated findings support the hypothesis.",
        ),
        limitations=(),
        provenance=(
            (
                "evaluation_plan_version",
                "hypothesis-evaluation-v1",
            ),
        ),
    )

    revision = (
        cli
        .run_comparative_hypothesis_evaluation_command
        ._promotion_application
        .run(
            evaluation=evaluation,
            knowledge_id="knowledge-rsi",
            statement=(
                "RSI effect persists across markets."
            ),
            applicability=("liquid FX",),
            limitations=("generated data",),
            provenance=(
                ("producer", "production-test"),
            ),
        )
    )

    rendered = (
        cli
        .generate_research_questions_command
        .execute(indent=None)
    )
    payload = json.loads(rendered)

    assert revision.item.id == "knowledge-rsi"
    assert revision.item.version == 1
    assert payload["artifact_type"] == (
        "knowledge_research_questions"
    )
    assert payload["question_count"] == 1
    assert len(payload["questions"]) == 1
    assert len(
        payload["snapshot_fingerprint"]
    ) == 64
