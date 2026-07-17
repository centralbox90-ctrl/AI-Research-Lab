from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
    MarketPositionDirection,
)
from src.research import ResearchEnvironmentRef
from src.application.research_artifact_serializer import (
    ResearchArtifactSerializer,
)


@dataclass
class FakeCycle:
    result: dict[str, Any]
    evaluation: dict[str, Any]
    statistical_evaluation: dict[str, Any]
    robustness_evaluation: dict[str, Any]
    contradiction_evaluation: dict[str, Any]
    evidence_strength_evaluation: dict[str, Any]
    hypothesis_decision: dict[str, Any]
    next_experiment_selection: dict[str, Any]
    evidence: dict[str, Any]
    analysis: dict[str, Any]
    conclusion: dict[str, Any]
    knowledge: dict[str, Any]


def build_cycle() -> FakeCycle:
    return FakeCycle(
        result={
            "id": "result-id",
        },
        evaluation={
            "valid": True,
        },
        statistical_evaluation={
            "significant": False,
        },
        robustness_evaluation={
            "robust": False,
        },
        contradiction_evaluation={
            "contradiction": False,
        },
        evidence_strength_evaluation={
            "score": 0.5,
        },
        hypothesis_decision={
            "supported": False,
        },
        next_experiment_selection={
            "action": "improve",
        },
        evidence={
            "source": "test",
        },
        analysis={
            "finding": "test",
        },
        conclusion={
            "supported": False,
        },
        knowledge={
            "statement": "test",
        },
    )


def build_specification() -> MarketExperimentSpecification:
    return MarketExperimentSpecification(
        executor_type="market_backtest",
        question_title="Test question",
        question_description="Test description",
        hypothesis_title="Test hypothesis",
        hypothesis_description="Test hypothesis description",
        expected_result="Positive result",
        experiment_title="Test experiment",
        experiment_description="Test experiment description",
        data_source="generated",
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
        stop_loss_percent=2.0,
        take_profit_percent=2.0,
        max_holding_bars=10,
        strategy_parameters={
            "test": True,
        },
        tags=(
            "artifact",
            "test",
        ),
    )

def build_research_environment() -> ResearchEnvironmentRef:
    return ResearchEnvironmentRef(
        dataset_fingerprint="dataset:001",
        assumption_set_fingerprint="assumptions:001",
        code_version="git:abc123",
        executor_version="backtest-engine:v1",
        statistical_method_version="statistics:v1",
        random_seed=42,
    )
def test_research_artifact_serializer_contains_specification_and_cycle():
    serializer = ResearchArtifactSerializer()

    artifact = serializer.serialize(
        specification=build_specification(),
        cycle=build_cycle(),
    )

    assert artifact["artifact_version"] == 1

    assert artifact["specification"]["symbol"] == "BTCUSDT"
    assert artifact["specification"]["direction"] == "LONG"

    assert artifact["cycle"]["result"]["id"] == "result-id"


def test_research_artifact_serializer_serializes_datetime_values():
    serializer = ResearchArtifactSerializer()

    artifact = serializer.serialize(
        specification=build_specification(),
        cycle=build_cycle(),
    )

    assert (
        artifact["specification"]["start_at"]
        == "2024-01-01T00:00:00+00:00"
    )

    assert (
        artifact["specification"]["end_at"]
        == "2024-02-01T00:00:00+00:00"
    )
def test_research_artifact_serializer_contains_environment():
    serializer = ResearchArtifactSerializer()

    environment = build_research_environment()

    artifact = serializer.serialize(
        specification=build_specification(),
        cycle=build_cycle(),
        research_environment=environment,
    )

    assert artifact["research_environment"] == {
        "dataset_fingerprint": "dataset:001",
        "assumption_set_fingerprint": "assumptions:001",
        "code_version": "git:abc123",
        "executor_version": "backtest-engine:v1",
        "statistical_method_version": "statistics:v1",
        "random_seed": 42,
        "fingerprint": environment.fingerprint(),
    }