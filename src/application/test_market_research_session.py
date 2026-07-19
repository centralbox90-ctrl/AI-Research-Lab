from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

import pandas as pd
import pytest

from src.application import (
    MarketExperimentSpecification,
    MarketPositionDirection,
)
from src.research.market_dataset_fingerprint import (
    DatasetFingerprintContext,
    MarketDatasetCanonicalizer,
    MarketDatasetFingerprinter,
)
from src.application.market_research_session import (
    MarketResearchSession,
)
from src.research import (
    AssumptionSet,
    Experiment,
    ExperimentResult,
    Hypothesis,
    Question,
    ResearchContext,
    ResearchEnvironmentRef,
)
from src.research.research_graph import (
    ResearchGraph,
)


class FakeExecutor:
    def __init__(self) -> None:
        self.called = False
        self.received: Experiment | None = None

    def __call__(
        self,
        experiment: Experiment,
    ) -> ExperimentResult:
        self.called = True
        self.received = experiment

        return ExperimentResult(
            experiment_id=experiment.id,
            success=True,
            metrics={"total_trades": 1},
            conclusion="ok",
        )


def build_specification() -> MarketExperimentSpecification:
    return MarketExperimentSpecification(
        executor_type="market_backtest",
        question_title="Question",
        question_description="Description",
        hypothesis_title="Hypothesis",
        hypothesis_description="Description",
        expected_result="Expected",
        experiment_title="Experiment",
        experiment_description="Description",
        data_source="test",
        symbol="EURUSD",
        timeframe="H1",
        start_at=datetime(
            2024,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        end_at=datetime(
            2024,
            1,
            2,
            tzinfo=timezone.utc,
        ),
        entry_rule="entry",
        exit_rule="exit",
        direction=MarketPositionDirection.LONG,
        stop_loss_percent=1.0,
        take_profit_percent=2.0,
        max_holding_bars=10,
    )


def build_context() -> ResearchContext:
    raw = pd.DataFrame(
        {
            "timestamp": [
                datetime(
                    2024,
                    1,
                    1,
                    tzinfo=timezone.utc,
                )
            ],
            "open": [1.0],
            "high": [1.1],
            "low": [0.9],
            "close": [1.05],
            "tick_volume": [100],
        }
    )

    data = MarketDatasetCanonicalizer().canonicalize(
        raw,
    )

    MarketDatasetFingerprinter().attach(
        data,
        DatasetFingerprintContext(
            symbol="EURUSD",
            timeframe="H1",
        ),
    )

    environment = ResearchEnvironmentRef(
        dataset_fingerprint=data.attrs[
            "dataset_fingerprint"
        ],
        assumption_set_fingerprint="assumptions",
        code_version="git:abc123",
        executor_version="backtest-engine:v1",
        statistical_method_version="statistics:v1",
        random_seed=42,
    )

    assumptions = AssumptionSet(
        id="assumptions",
        assumptions=(),
    )

    return ResearchContext(
        specification=build_specification(),
        environment=environment,
        market_data=data,
        assumptions=assumptions,
    )


def build_question() -> Question:
    return Question(
        title="Question",
    )


def build_hypothesis(
    question: Question,
) -> Hypothesis:
    return Hypothesis(
        question_id=question.id,
        title="Hypothesis",
    )


def test_session_executes_executor() -> None:
    question = build_question()
    hypothesis = build_hypothesis(
        question,
    )

    experiment = Experiment(
        hypothesis_id=hypothesis.id,
        title="session test",
    )

    executor = FakeExecutor()

    graph = ResearchGraph(
        question=question,
        hypothesis=hypothesis,
        experiment=experiment,
    )

    session = MarketResearchSession(
        context=build_context(),
        graph=graph,
        executor=executor,
    )

    result = session.execute()

    assert executor.called is True
    assert executor.received is experiment
    assert result.success is True
    assert result.experiment_id == experiment.id

    assert session.graph is graph
    assert session.graph.question is question
    assert session.graph.hypothesis is hypothesis
    assert session.graph.experiment is experiment


def test_session_is_immutable() -> None:
    question = build_question()
    hypothesis = build_hypothesis(
        question,
    )

    experiment = Experiment(
        hypothesis_id=hypothesis.id,
        title="immutable",
    )

    session = MarketResearchSession(
        context=build_context(),
        graph=ResearchGraph(
            question=question,
            hypothesis=hypothesis,
            experiment=experiment,
        ),
        executor=FakeExecutor(),
    )

    replacement_graph = ResearchGraph(
        question=question,
        hypothesis=hypothesis,
        experiment=Experiment(
            hypothesis_id=hypothesis.id,
            title="changed",
        ),
    )

    with pytest.raises(FrozenInstanceError):
        session.graph = replacement_graph


def test_session_rejects_inconsistent_graph() -> None:
    question = build_question()

    hypothesis = Hypothesis(
        question_id="different-question",
        title="Hypothesis",
    )

    experiment = Experiment(
        hypothesis_id=hypothesis.id,
        title="Experiment",
    )

    graph = ResearchGraph(
        question=question,
        hypothesis=hypothesis,
        experiment=experiment,
    )

    with pytest.raises(
        ValueError,
        match="hypothesis does not belong to session question",
    ):
        MarketResearchSession(
            context=build_context(),
            graph=graph,
            executor=FakeExecutor(),
        )


def test_session_rejects_experiment_from_other_hypothesis() -> None:
    question = build_question()
    hypothesis = build_hypothesis(
        question,
    )

    experiment = Experiment(
        hypothesis_id="different-hypothesis",
        title="Experiment",
    )

    graph = ResearchGraph(
        question=question,
        hypothesis=hypothesis,
        experiment=experiment,
    )

    with pytest.raises(
        ValueError,
        match="experiment does not belong to session hypothesis",
    ):
        MarketResearchSession(
            context=build_context(),
            graph=graph,
            executor=FakeExecutor(),
        )
