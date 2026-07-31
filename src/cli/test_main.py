import json
import sqlite3
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path

from src.application.hypothesis_evaluation_artifact_envelope_factory import (
    HypothesisEvaluationArtifactEnvelopeFactory,
)
from src.application.knowledge_research_questions_artifact_envelope_factory import (
    KnowledgeResearchQuestionsArtifactEnvelopeFactory,
)
from src.application.market_research_campaign_artifact_envelope_factory import (
    MarketResearchCampaignArtifactEnvelopeFactory,
)
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


def test_main_reports_corrupt_research_cycle(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "research_cycles.db"
    store = SqliteResearchCycleStore(
        db_path=db_path,
    )
    store.save(
        result_id="result-corrupted",
        serialized_cycle={
            "result": {
                "id": "different-result",
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
            "result-corrupted",
        ],
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 1
    assert stdout.getvalue() == ""
    assert stderr.getvalue() == (
        "Unable to get research cycle: "
        "stored research artifact 'result-corrupted' "
        "failed integrity validation: "
        "legacy research cycle result id does "
        "not match storage key\n"
    )


def test_main_rejects_corrupt_research_artifact_export(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "research_cycles.db"
    output_path = tmp_path / "artifact.json"
    store = SqliteResearchCycleStore(
        db_path=db_path,
    )
    store.save(
        result_id="result-corrupted",
        serialized_cycle={
            "result": {
                "id": "different-result",
            },
        },
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        [
            "--database",
            str(db_path),
            "export-research-artifact",
            "result-corrupted",
            "--output",
            str(output_path),
        ],
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 1
    assert stdout.getvalue() == ""
    assert not output_path.exists()
    assert stderr.getvalue() == (
        "Unable to export research artifact: "
        "stored research artifact 'result-corrupted' "
        "failed integrity validation: "
        "legacy research cycle result id does "
        "not match storage key\n"
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
    assert isinstance(
        command._artifact_envelope_factory,
        HypothesisEvaluationArtifactEnvelopeFactory,
    )
    assert (
        command
        ._promotion_application
        ._knowledge_repository
        is
        cli.generate_research_questions_command
        ._application
        ._snapshot_builder
        ._knowledge_repository
    )


def test_build_research_cli_configures_campaign_command(
    tmp_path: Path,
) -> None:
    cli = build_research_cli(
        db_path=tmp_path / "research_cycles.db",
    )

    command = (
        cli.run_market_research_campaign_command
    )

    assert isinstance(
        command,
        RunMarketResearchCampaignCommand,
    )
    assert isinstance(
        command._artifact_envelope_factory,
        MarketResearchCampaignArtifactEnvelopeFactory,
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
    assert isinstance(
        cli.generate_research_questions_command
        ._artifact_envelope_factory,
        KnowledgeResearchQuestionsArtifactEnvelopeFactory,
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
            "--correlation-id",
            "knowledge-lifecycle-42",
        ],
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 0
    assert stderr.getvalue() == ""

    payload = json.loads(stdout.getvalue())

    assert payload["schema_version"] == 1
    assert payload["artifact_type"] == (
        "knowledge_research_questions"
    )
    assert payload[
        "payload_schema_version"
    ] == 1
    assert payload["correlation_id"] == (
        "knowledge-lifecycle-42"
    )
    assert payload["payload"][
        "question_count"
    ] == 1
    assert len(
        payload["payload"]["questions"]
    ) == 1
    assert len(
        payload["payload"][
            "snapshot_fingerprint"
        ]
    ) == 64
    assert payload["payload"]["snapshot"][
        "schema_version"
    ] == 1


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
    assert payload["schema_version"] == 1
    assert payload["artifact_type"] == (
        "knowledge_research_questions"
    )
    assert payload[
        "payload_schema_version"
    ] == 1
    assert payload["payload"][
        "question_count"
    ] == 1
    assert len(
        payload["payload"]["questions"]
    ) == 1
    assert len(
        payload["payload"][
            "snapshot_fingerprint"
        ]
    ) == 64
    assert payload["payload"]["snapshot"][
        "schema_version"
    ] == 1

def build_comparative_market_specification_payload(
    *,
    start_at: str,
    end_at: str,
    experiment_title: str,
) -> dict[str, object]:
    return {
        "executor_type": "market_backtest",
        "question_title": (
            "Does RSI predict forward returns?"
        ),
        "question_description": (
            "Evaluate RSI over distinct generated periods."
        ),
        "hypothesis_title": (
            "RSI oversold values precede positive returns"
        ),
        "hypothesis_description": (
            "Replicated RSI observations should support "
            "positive forward returns."
        ),
        "expected_result": (
            "Positive replicated comparative evidence."
        ),
        "experiment_title": experiment_title,
        "experiment_description": (
            "Analyze one declared generated period."
        ),
        "data_source": "generated",
        "symbol": "EURUSD",
        "timeframe": "H1",
        "start_at": start_at,
        "end_at": end_at,
        "entry_rule": "rsi < 30",
        "exit_rule": "rsi > 50",
        "direction": "LONG",
        "stop_loss_percent": 1.0,
        "take_profit_percent": 2.0,
        "max_holding_bars": 10,
    }


def test_main_runs_real_comparative_request_to_evaluation(
    tmp_path: Path,
) -> None:
    first_specification = (
        build_comparative_market_specification_payload(
            start_at=(
                "2026-01-01T00:00:00Z"
            ),
            end_at=(
                "2026-07-01T00:00:00Z"
            ),
            experiment_title=(
                "RSI generated replication one"
            ),
        )
    )
    second_specification = (
        build_comparative_market_specification_payload(
            start_at=(
                "2026-07-01T00:00:00Z"
            ),
            end_at=(
                "2027-01-01T00:00:00Z"
            ),
            experiment_title=(
                "RSI generated replication two"
            ),
        )
    )
    request_payload = {
        "hypothesis_id": "hypothesis-rsi",
        "correlation_id": (
            "comparative-production-42"
        ),
        "requests": [
            {
                "market_specifications": [
                    first_specification,
                    second_specification,
                ],
                "indicator_id": "rsi",
                "outcome_specification": {
                    "horizons": [1, 3],
                    "price_field": "close",
                },
                "horizon": 1,
                "statement": (
                    "RSI supports one-bar returns."
                ),
                "applicable_markets": [
                    "EURUSD:H1",
                ],
            },
            {
                "market_specifications": [
                    first_specification,
                    second_specification,
                ],
                "indicator_id": "rsi",
                "outcome_specification": {
                    "horizons": [1, 3],
                    "price_field": "close",
                },
                "horizon": 3,
                "statement": (
                    "RSI supports three-bar returns."
                ),
                "applicable_markets": [
                    "EURUSD:H1",
                ],
            },
        ],
    }
    request_path = (
        tmp_path / "comparative-request.json"
    )
    request_path.write_text(
        json.dumps(
            request_payload,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    database_path = (
        tmp_path / "research-cycles.db"
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        [
            "--database",
            str(database_path),
            "run-comparative-hypothesis-evaluation",
            "--request",
            str(request_path),
            "--compact",
        ],
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 0, stderr.getvalue()
    assert stderr.getvalue() == ""

    artifact = json.loads(
        stdout.getvalue()
    )
    evaluation = artifact["payload"][
        "evaluation"
    ]

    assert artifact["schema_version"] == 1
    assert artifact["artifact_type"] == (
        "hypothesis_evaluation"
    )
    assert artifact["payload_schema_version"] == 1
    assert artifact["producer"] == (
        "comparative-hypothesis-evaluation"
    )
    assert artifact["correlation_id"] == (
        "comparative-production-42"
    )
    assert evaluation["hypothesis_id"] == (
        "hypothesis-rsi"
    )
    assert evaluation["state"] == (
        "inconclusive"
    )
    assert evaluation["confidence"] == 0.0
    assert len(evaluation["finding_refs"]) == 2
    assert len(artifact["source_references"]) == 1

    with sqlite3.connect(
        database_path
    ) as connection:
        execution_rows = connection.execute(
            """
            SELECT
                execution_id,
                sequence,
                status,
                payload
            FROM experiment_execution_snapshots
            ORDER BY execution_id, sequence
            """
        ).fetchall()

    assert len(execution_rows) == 12

    execution_histories = {}

    for (
        execution_id,
        sequence,
        status,
        serialized_payload,
    ) in execution_rows:
        execution_histories.setdefault(
            execution_id,
            [],
        ).append(
            (
                sequence,
                status,
                json.loads(serialized_payload),
            )
        )

    assert len(execution_histories) == 4

    for history in execution_histories.values():
        assert [
            snapshot[0]
            for snapshot in history
        ] == [1, 2, 3]
        assert [
            snapshot[1]
            for snapshot in history
        ] == [
            "PENDING",
            "RUNNING",
            "SUCCEEDED",
        ]

        payloads = [
            snapshot[2]
            for snapshot in history
        ]

        assert [
            payload["status"]
            for payload in payloads
        ] == [
            "PENDING",
            "RUNNING",
            "SUCCEEDED",
        ]
        assert all(
            payload["correlation_id"]
            == "comparative-production-42"
            for payload in payloads
        )
        assert all(
            payload["failure"] is None
            for payload in payloads
        )
        assert (
            payloads[2]["result_id"]
            is not None
        )

def test_main_persists_failed_comparative_execution(
    tmp_path: Path,
) -> None:
    first_specification = (
        build_comparative_market_specification_payload(
            start_at=(
                "2026-01-01T00:00:00Z"
            ),
            end_at=(
                "2026-01-01T01:00:00Z"
            ),
            experiment_title=(
                "Insufficient comparative replication one"
            ),
        )
    )
    second_specification = (
        build_comparative_market_specification_payload(
            start_at=(
                "2026-02-01T00:00:00Z"
            ),
            end_at=(
                "2026-02-01T01:00:00Z"
            ),
            experiment_title=(
                "Insufficient comparative replication two"
            ),
        )
    )
    request_payload = {
        "hypothesis_id": "hypothesis-rsi-failure",
        "correlation_id": (
            "comparative-failure-42"
        ),
        "requests": [
            {
                "market_specifications": [
                    first_specification,
                    second_specification,
                ],
                "indicator_id": "rsi",
                "outcome_specification": {
                    "horizons": [1],
                    "price_field": "close",
                },
                "horizon": 1,
                "statement": (
                    "Insufficient data should fail "
                    "comparative execution."
                ),
                "applicable_markets": [
                    "EURUSD:H1",
                ],
            },
        ],
    }
    request_path = (
        tmp_path / "failed-comparative-request.json"
    )
    request_path.write_text(
        json.dumps(
            request_payload,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    database_path = (
        tmp_path / "research-cycles.db"
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        [
            "--database",
            str(database_path),
            "run-comparative-hypothesis-evaluation",
            "--request",
            str(request_path),
            "--compact",
        ],
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 1
    assert stdout.getvalue() == ""
    assert stderr.getvalue() == (
        "Unable to run comparative hypothesis "
        "evaluation: warmup_bars must not "
        "exceed series length\n"
    )

    with sqlite3.connect(
        database_path
    ) as connection:
        execution_rows = connection.execute(
            """
            SELECT
                execution_id,
                sequence,
                status,
                payload
            FROM experiment_execution_snapshots
            ORDER BY sequence
            """
        ).fetchall()

    assert len(execution_rows) == 3
    assert len(
        {
            row[0]
            for row in execution_rows
        }
    ) == 1
    assert [
        row[1]
        for row in execution_rows
    ] == [1, 2, 3]
    assert [
        row[2]
        for row in execution_rows
    ] == [
        "PENDING",
        "RUNNING",
        "FAILED",
    ]

    payloads = [
        json.loads(row[3])
        for row in execution_rows
    ]

    assert [
        payload["status"]
        for payload in payloads
    ] == [
        "PENDING",
        "RUNNING",
        "FAILED",
    ]
    assert all(
        payload["correlation_id"]
        == "comparative-failure-42"
        for payload in payloads
    )

    pending, running, failed = payloads

    assert pending[
        "specification_fingerprint"
    ] == running[
        "specification_fingerprint"
    ]
    assert failed[
        "specification_fingerprint"
    ] == running[
        "specification_fingerprint"
    ]
    assert failed[
        "environment_fingerprint"
    ] == running[
        "environment_fingerprint"
    ]
    assert failed["result_id"] is None
    assert failed["failure"] == {
        "stage": "EXECUTION",
        "error_type": "ValueError",
        "message": (
            "warmup_bars must not exceed "
            "series length"
        ),
    }
