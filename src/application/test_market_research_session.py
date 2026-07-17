from datetime import datetime, timezone

import pandas as pd
import pytest

from src.application import (
    MarketExperimentSpecification,
    MarketPositionDirection,
)
from src.application.market_dataset_fingerprint import (
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


class FakeExecutor:
    def __init__(self) -> None:
        self.called = False
        self.received = None

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

    data = (
        MarketDatasetCanonicalizer()
        .canonicalize(raw)
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
    hypothesis = build_hypothesis(question)
    executor = FakeExecutor()

    experiment = Experiment(
        hypothesis_id=hypothesis.id,
        title="session test",
    )

    session = MarketResearchSession(
        context=build_context(),
        question=question,
        hypothesis=hypothesis,
        experiment=experiment,
        executor=executor,
    )

    result = session.execute()

    assert executor.called is True
    assert executor.received is experiment
    assert result.success is True
    assert result.experiment_id == experiment.id


def test_session_is_immutable() -> None:
    question = build_question()
    hypothesis = build_hypothesis(question)

    session = MarketResearchSession(
        context=build_context(),
        question=question,
        hypothesis=hypothesis,
        experiment=Experiment(
            hypothesis_id=hypothesis.id,
            title="immutable",
        ),
        executor=FakeExecutor(),
    )

    try:
        session.experiment = Experiment(
            hypothesis_id=hypothesis.id,
            title="changed",
        )
        assert False
    except Exception:
        pass
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

    with pytest.raises(
        ValueError,
        match="question",
    ):
        MarketResearchSession(
            context=build_context(),
            question=question,
            hypothesis=hypothesis,
            experiment=experiment,
            executor=FakeExecutor(),
        )