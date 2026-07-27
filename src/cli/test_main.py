import json
from io import StringIO
from pathlib import Path

from src.cli import (
    build_research_cli,
    main,
)
from src.cli.generate_research_questions_from_knowledge_snapshot_command import (
    GenerateResearchQuestionsFromKnowledgeSnapshotCommand,
)
from src.cli.run_indicator_comparative_hypothesis_evaluation_command import (
    RunIndicatorComparativeHypothesisEvaluationCommand,
)
from src.cli.run_market_research_campaign_command import (
    RunMarketResearchCampaignCommand,
)
from src.storage import SqliteResearchCycleStore


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

    assert isinstance(
        cli.run_comparative_hypothesis_evaluation_command,
        RunIndicatorComparativeHypothesisEvaluationCommand,
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
        GenerateResearchQuestionsFromKnowledgeSnapshotCommand,
    )


def test_main_generates_questions_from_knowledge_snapshot(
    tmp_path: Path,
) -> None:
    snapshot_path = (
        tmp_path / "knowledge-snapshot.json"
    )
    snapshot_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "items": [],
                "relations": [],
            }
        ),
        encoding="utf-8",
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        [
            "--database",
            str(tmp_path / "research-cycles.db"),
            "generate-knowledge-research-questions",
            "--snapshot",
            str(snapshot_path),
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
    assert payload["question_count"] == 0
    assert payload["questions"] == []
    assert len(
        payload["snapshot_fingerprint"]
    ) == 64