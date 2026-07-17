from pathlib import Path

from src.application import RunAndStoreSerializedResearchCycle
from src.research import (
    Experiment,
    ExperimentResult,
    Hypothesis,
    Question,
)
from src.storage import SqliteResearchCycleStore


def test_run_and_store_serialized_research_cycle_persists_payload(
    tmp_path: Path,
) -> None:
    question = Question(
        title="Can a completed cycle be stored in SQLite?",
    )

    hypothesis = Hypothesis(
        question_id=question.id,
        title="Completed cycles can be serialized and persisted",
    )

    experiment = Experiment(
        hypothesis_id=hypothesis.id,
        title="SQLite application persistence experiment",
    )

    def execute(current_experiment: Experiment) -> ExperimentResult:
        return ExperimentResult(
            experiment_id=current_experiment.id,
            success=True,
            metrics={
                "net_profit": 10.0,
                "total_trades": 5,
            },
            observations={
                "profit_percent": [
                    1.8,
                    2.0,
                    2.1,
                    1.9,
                    2.2,
                ],
            },
            conclusion="A stable positive effect was observed.",
        )

    store = SqliteResearchCycleStore(
        db_path=tmp_path / "research_cycles.db",
    )

    use_case = RunAndStoreSerializedResearchCycle(
        store=store,
    )

    cycle = use_case.execute(
        question=question,
        hypothesis=hypothesis,
        experiment=experiment,
        executor=execute,
    )

    stored = store.get(cycle.result.id)

    assert stored is not None
    assert stored["result"]["id"] == cycle.result.id
    assert stored["result"]["success"] is True

    assert (
        stored["evidence_strength_evaluation"]["level"]
        == "very_strong"
    )

    assert stored["hypothesis_decision"]["is_supported"] is True

    assert (
        stored["next_experiment_selection"]["action"]
        == "replicate_experiment"
    )

    assert stored["conclusion"]["supported"] is True
    assert stored["knowledge"]["is_provisional"] is False