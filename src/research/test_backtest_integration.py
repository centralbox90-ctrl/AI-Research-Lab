import pandas as pd

from src.research.backtest_executor import BacktestExperimentExecutor
from src.research.engine import ResearchEngine
from src.research.experiment import Experiment
from src.research.hypothesis import Hypothesis
from src.research.question import Question


def test_research_engine_runs_backtest_experiment() -> None:
    question = Question(title="Backtest research")

    hypothesis = Hypothesis(
        question_id=question.id,
        title="Strategy is profitable",
    )

    experiment = Experiment(
        hypothesis_id=hypothesis.id,
        title="BTCUSDT backtest",
    )

    def data_provider(current_experiment: Experiment) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "timestamp": pd.date_range(
                    "2026-01-01",
                    periods=3,
                    freq="h",
                ),
                "close": [100.0, 105.0, 110.0],
                "high": [101.0, 106.0, 111.0],
                "low": [99.0, 104.0, 109.0],
                "AI_prediction": [1, 1, 0],
            }
        )

    executor = BacktestExperimentExecutor(
        data_provider=data_provider,
        symbol="BTCUSDT",
        timeframe="1H",
    )

    result, evidence, analysis, conclusion, knowledge = (
        ResearchEngine().run(
            question=question,
            hypothesis=hypothesis,
            experiment=experiment,
            executor=executor,
        )
    )

    assert result.success is True
    assert result.metrics["total_trades"] == 1
    assert result.metrics["net_profit"] == 10.0
    assert evidence.data == result.metrics
    assert conclusion.supported is True
    assert knowledge.statement == "Hypothesis supported"
