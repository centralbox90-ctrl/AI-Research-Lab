from datetime import datetime, timezone
from pathlib import Path

import pytest

from src.application import (
    MarketExperimentExecutor,
    MarketExperimentSpecification,
    MarketPositionDirection,
    RunAndStoreResearchArtifact,
    RunMarketResearch,
)
from src.research import (
    Experiment,
    ExperimentResult,
    Hypothesis,
    NextExperimentResearchCycleResult,
    Question,
    ResearchEnvironmentRef,
)
from src.storage import SqliteResearchCycleStore


class SuccessfulMarketExecutor:
    def __init__(self) -> None:
        self.received_experiment: Experiment | None = None

    def __call__(
        self,
        experiment: Experiment,
    ) -> ExperimentResult:
        self.received_experiment = experiment

        return ExperimentResult(
            experiment_id=experiment.id,
            success=True,
            metrics={
                "net_profit": 10.0,
                "total_trades": 5.0,
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
            conclusion=(
                "A stable positive effect was observed."
            ),
        )

class FakeContext:
    def __init__(
        self,
        *,
        environment: ResearchEnvironmentRef,
    ) -> None:
        self.environment = environment


class FakeSession:
    def __init__(
        self,
        *,
        context: FakeContext,
        question: Question,
        hypothesis: Hypothesis,
        experiment: Experiment,
        executor: MarketExperimentExecutor,
    ) -> None:
        self.context = context
        self.question = question
        self.hypothesis = hypothesis
        self.experiment = experiment
        self.executor = executor


class RecordingSessionFactory:
    def __init__(
        self,
        session: FakeSession,
    ) -> None:
        self.session = session

        self.received_specification: (
            MarketExperimentSpecification | None
        ) = None

    def create(
        self,
        specification: MarketExperimentSpecification,
    ) -> FakeSession:
        self.received_specification = specification

        return self.session


def build_specification() -> MarketExperimentSpecification:
    return MarketExperimentSpecification(
        executor_type="market_backtest",
        question_title=(
            "Does Williams oversold predict a rebound?"
        ),
        question_description=(
            "Test whether a Williams oversold condition is followed "
            "by positive historical trade returns."
        ),
        hypothesis_title=(
            "Williams oversold values precede positive returns"
        ),
        hypothesis_description=(
            "BTCUSDT should produce positive trade results after "
            "the registered Williams oversold condition."
        ),
        expected_result=(
            "Positive net profit with a non-zero number of trades."
        ),
        experiment_title=(
            "Williams BTCUSDT historical backtest"
        ),
        experiment_description=(
            "Run registered entry and exit rules on historical "
            "BTCUSDT data."
        ),
        data_source="historical_csv",
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
            12,
            31,
            tzinfo=timezone.utc,
        ),
        entry_rule="williams_oversold_entry",
        exit_rule="stop_take_or_max_holding_exit",
        direction=MarketPositionDirection.LONG,
        stop_loss_percent=1.0,
        take_profit_percent=2.0,
        max_holding_bars=24,
        commission_percent=0.1,
        slippage_percent=0.05,
        strategy_parameters={
            "williams_period": 14,
            "oversold_level": -80,
        },
        tags=(
            "btc",
            "williams",
            "historical-backtest",
        ),
    )


def test_run_market_research_uses_reproducible_session(
    tmp_path: Path,
) -> None:
    specification = build_specification()

    question = Question(
        title=specification.question_title,
        description=specification.question_description,
    )

    hypothesis = Hypothesis(
        question_id=question.id,
        title=specification.hypothesis_title,
        description=(
            specification.hypothesis_description
        ),
        expected_result=specification.expected_result,
    )

    experiment = Experiment(
        hypothesis_id=hypothesis.id,
        title=specification.experiment_title,
        description=(
            specification.experiment_description
        ),
        parameters={
            "symbol": specification.symbol,
            "strategy_parameters": (
                specification.strategy_parameters
            ),
        },
    )

    executor = SuccessfulMarketExecutor()

    environment = ResearchEnvironmentRef(
        dataset_fingerprint="dataset:001",
        assumption_set_fingerprint="assumptions:001",
        code_version="git:abc123",
        executor_version="backtest-engine:v1",
        statistical_method_version="statistics:v1",
        random_seed=123,
    )

    context = FakeContext(
        environment=environment,
    )

    session = FakeSession(
        context=context,
        question=question,
        hypothesis=hypothesis,
        experiment=experiment,
        executor=executor,
    )

    session_factory = RecordingSessionFactory(
        session=session,
    )

    store = SqliteResearchCycleStore(
        db_path=tmp_path / "research_cycles.db",
    )

    use_case = RunMarketResearch(
        run_and_store=RunAndStoreResearchArtifact(
            store=store,
        ),
        session_factory=session_factory,
    )

    cycle = use_case.execute(
        specification,
    )

    assert (
        session_factory.received_specification
        is specification
    )

    assert executor.received_experiment is experiment

    assert (
        cycle.result.experiment_id
        == experiment.id
    )

    assert cycle.result.success is True

    stored = store.get(
        cycle.result.id,
    )

    assert stored is not None

    assert stored["research_environment"] == {
        "dataset_fingerprint": "dataset:001",
        "assumption_set_fingerprint": (
            "assumptions:001"
        ),
        "code_version": "git:abc123",
        "executor_version": "backtest-engine:v1",
        "statistical_method_version": (
            "statistics:v1"
        ),
        "random_seed": 123,
        "fingerprint": environment.fingerprint(),
    }
