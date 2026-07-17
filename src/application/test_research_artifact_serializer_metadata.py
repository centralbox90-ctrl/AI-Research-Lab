from datetime import datetime, UTC

from src.application.artifact_metadata import (
    ArtifactMetadata,
)
from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
    MarketPositionDirection,
)
from src.application.research_artifact_serializer import (
    ResearchArtifactSerializer,
)


class FakeCycle(dict):

    def __init__(self):
        super().__init__(
            {
                "result": {
                    "id": "result-id",
                },
                "evaluation": {},
                "statistical_evaluation": {},
                "robustness_evaluation": {},
                "contradiction_evaluation": {},
                "evidence_strength_evaluation": {},
                "hypothesis_decision": {},
                "next_experiment_selection": {},
                "evidence": {},
                "analysis": {},
                "conclusion": {},
                "knowledge": {},
            }
        )


def build_metadata() -> ArtifactMetadata:
    return ArtifactMetadata(
        artifact_id="artifact-001",
        schema_version="1.0",
        created_at=datetime.now(UTC),
        experiment_id="experiment-001",
        executor_type="market_backtest_executor",
        executor_version="1.0",
        data_source="BTCUSDT_1H",
        code_version="abc123",
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
            tzinfo=UTC,
        ),
        end_at=datetime(
            2024,
            2,
            1,
            tzinfo=UTC,
        ),
        entry_rule="entry",
        exit_rule="exit",
        direction=MarketPositionDirection.LONG,
        stop_loss_percent=2.0,
        take_profit_percent=2.0,
        max_holding_bars=10,
        strategy_parameters={},
        tags=(),
    )


def test_research_artifact_serializer_serializes_metadata():

    serializer = ResearchArtifactSerializer()

    artifact = serializer.serialize(
        specification=build_specification(),
        cycle=FakeCycle(),
        metadata=build_metadata(),
    )

    assert artifact["metadata"]["artifact_id"] == "artifact-001"
    assert artifact["metadata"]["schema_version"] == "1.0"
    assert (
        artifact["metadata"]["experiment_id"]
        == "experiment-001"
    )
    assert (
        artifact["metadata"]["data_source"]
        == "BTCUSDT_1H"
    )
    assert (
        artifact["metadata"]["code_version"]
        == "abc123"
    )