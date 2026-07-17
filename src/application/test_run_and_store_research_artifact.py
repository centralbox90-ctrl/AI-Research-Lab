from datetime import datetime, timezone
from pathlib import Path

from src.application.artifact_lineage import (
    ArtifactLineage,
)
from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
    MarketPositionDirection,
)
from src.application.run_and_store_research_artifact import (
    RunAndStoreResearchArtifact,
)
from src.research import (
    Experiment,
    ExperimentResult,
    Hypothesis,
    Question,
)
from src.storage import SqliteResearchCycleStore


class SuccessfulExecutor:
    def __call__(
        self,
        experiment: Experiment,
    ) -> ExperimentResult:
        return ExperimentResult(
            experiment_id=experiment.id,
            success=True,
            metrics={
                "net_profit": 10.0,
                "total_trades": 5,
            },
            observations={
                "profit_percent": [
                    1.0,
                    2.0,
                ],
            },
            conclusion="Positive result.",
        )


def build_specification():
    return MarketExperimentSpecification(
        executor_type="market_backtest",
        question_title="Artifact test question",
        question_description="Test",
        hypothesis_title="Artifact hypothesis",
        hypothesis_description="Test",
        expected_result="Positive",
        experiment_title="Artifact experiment",
        experiment_description="Test",
        data_source="test",
        symbol="BTCUSDT",
        timeframe="1h",
        start_at=datetime(
            2024,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        end_at=datetime(
            2024,
            2,
            1,
            tzinfo=timezone.utc,
        ),
        entry_rule="entry",
        exit_rule="exit",
        direction=MarketPositionDirection.LONG,
        stop_loss_percent=1.0,
        take_profit_percent=2.0,
        max_holding_bars=10,
    )


def build_research_entities():
    question = Question(
        title="Question",
        description="Description",
    )

    hypothesis = Hypothesis(
        question_id=question.id,
        title="Hypothesis",
        description="Description",
        expected_result="Positive",
    )

    experiment = Experiment(
        hypothesis_id=hypothesis.id,
        title="Experiment",
        description="Description",
    )

    return question, hypothesis, experiment


def test_run_and_store_research_artifact_persists_artifact(
    tmp_path: Path,
):
    store = SqliteResearchCycleStore(
        db_path=tmp_path / "research.db",
    )

    use_case = RunAndStoreResearchArtifact(
        store=store,
    )

    question, hypothesis, experiment = (
        build_research_entities()
    )

    cycle = use_case.execute(
        specification=build_specification(),
        question=question,
        hypothesis=hypothesis,
        experiment=experiment,
        executor=SuccessfulExecutor(),
    )

    stored = store.get(
        cycle.result.id,
    )

    assert stored is not None
    assert stored["artifact_version"] == 1
    assert stored["specification"]["symbol"] == "BTCUSDT"
    assert stored["cycle"]["result"]["id"] == cycle.result.id
    assert "lineage" not in stored


def test_run_and_store_research_artifact_persists_lineage(
    tmp_path: Path,
):
    database_path = tmp_path / "research.db"

    store = SqliteResearchCycleStore(
        db_path=database_path,
    )

    use_case = RunAndStoreResearchArtifact(
        store=store,
    )

    question, hypothesis, experiment = (
        build_research_entities()
    )

    lineage = ArtifactLineage(
        parent_artifact_id="parent-artifact-001",
        lineage_type="derived_from",
        change_description=(
            "Executed the selected next experiment."
        ),
        created_from_experiment=str(experiment.id),
    )

    cycle = use_case.execute(
        specification=build_specification(),
        question=question,
        hypothesis=hypothesis,
        experiment=experiment,
        executor=SuccessfulExecutor(),
        lineage=lineage,
    )

    reopened_store = SqliteResearchCycleStore(
        db_path=database_path,
    )

    stored = reopened_store.get(
        cycle.result.id,
    )

    assert stored is not None

    assert stored["lineage"] == {
        "parent_artifact_id": "parent-artifact-001",
        "lineage_type": "derived_from",
        "change_description": (
            "Executed the selected next experiment."
        ),
        "created_from_experiment": str(experiment.id),
    }