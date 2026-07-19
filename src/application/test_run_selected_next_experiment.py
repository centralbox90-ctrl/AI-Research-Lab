from datetime import datetime, timezone
from pathlib import Path

from src.application.get_stored_research_artifact import (
    GetStoredResearchArtifact,
)
from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
    MarketPositionDirection,
)
from src.application.run_and_store_research_artifact import (
    RunAndStoreResearchArtifact,
)
from src.application.run_selected_next_experiment import (
    RunSelectedNextExperiment,
)
from src.research import (
    Experiment,
    ExperimentResult,
    Hypothesis,
    NextExperimentSelection,
    Question,
    ResearchEnvironmentRef,
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
            observations={},
            conclusion="Positive result.",
        )


def build_specification():
    return MarketExperimentSpecification(
        executor_type="market_backtest",
        question_title="Lineage question",
        question_description="Test",
        hypothesis_title="Lineage hypothesis",
        hypothesis_description="Test",
        expected_result="Positive",
        experiment_title="Lineage experiment",
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

def build_research_environment() -> ResearchEnvironmentRef:
    return ResearchEnvironmentRef(
        dataset_fingerprint="dataset-fingerprint-001",
        assumption_set_fingerprint=(
            "assumption-set-fingerprint-001"
        ),
        code_version="git:test-commit",
        executor_version="backtest-engine:test",
        statistical_method_version="statistics:test",
        random_seed=42,
    )

def test_run_selected_next_experiment_persists_child_lineage(
    tmp_path: Path,
):
    database_path = tmp_path / "research.db"

    store = SqliteResearchCycleStore(
        db_path=database_path,
    )

    artifact_runner = RunAndStoreResearchArtifact(
        store=store,
    )

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

    parent_experiment = Experiment(
        hypothesis_id=hypothesis.id,
        title="Parent experiment",
        description="Initial validation",
        parameters={
            "sample_size": 500,
        },
    )

    parent_cycle = artifact_runner.execute(
        specification=build_specification(),
        question=question,
        hypothesis=hypothesis,
        experiment=parent_experiment,
        executor=SuccessfulExecutor(),
        research_environment=build_research_environment(),
    )

    parent_artifact = store.get(
        parent_cycle.result.id,
    )

    assert parent_artifact is not None

    parent_artifact_id = (
        parent_artifact["metadata"]["artifact_id"]
    )

    selection = NextExperimentSelection(
        hypothesis_id=hypothesis.id,
        is_selected=True,
        action="increase_sample_size",
        priority="high",
        reason="Sample size requirement failed.",
        target_requirement="sample_size",
    )

    use_case = RunSelectedNextExperiment(
        artifact_getter=GetStoredResearchArtifact(
            store=store,
        ),
        artifact_runner=artifact_runner,
    )

    child_cycle = use_case.execute(
        parent_result_id=parent_cycle.result.id,
        specification=build_specification(),
        question=question,
        hypothesis=hypothesis,
        parent_experiment=parent_experiment,
        selection=selection,
        research_environment=build_research_environment(),
        executor=SuccessfulExecutor(),
    )

    reopened_store = SqliteResearchCycleStore(
        db_path=database_path,
    )

    child_artifact = reopened_store.get(
        child_cycle.result.id,
    )

    assert child_artifact is not None

    assert (
        child_artifact["metadata"]["artifact_id"]
        != parent_artifact_id
    )

    assert child_artifact["lineage"][
        "parent_artifact_id"
    ] == parent_artifact_id

    assert (
        child_artifact["lineage"]["lineage_type"]
        == "derived_from"
    )

    assert (
        child_artifact["lineage"]["change_description"]
        == (
            "Executed selected next research action: "
            "increase_sample_size."
        )
    )

    assert (
        child_artifact["lineage"][
            "created_from_experiment"
        ]
        == child_artifact["metadata"]["experiment_id"]
    )

    assert (
        child_artifact["cycle"]["result"]["experiment_id"]
        == child_artifact["metadata"]["experiment_id"]
    )