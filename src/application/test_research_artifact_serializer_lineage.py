from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from src.application.artifact_lineage import (
    ArtifactLineage,
)
from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
    MarketPositionDirection,
)
from src.application.research_artifact_serializer import (
    ResearchArtifactSerializer,
)


@dataclass
class FakeCycle:
    result: dict[str, Any]

    def __init__(self):
        self.result = {
            "id": "result-id",
        }


def build_lineage() -> ArtifactLineage:
    return ArtifactLineage(
        parent_artifact_id="artifact-000",
        lineage_type="derived_from",
        change_description="Added ADX confirmation feature",
        created_from_experiment="experiment-002",
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
        strategy_parameters={},
        tags=(),
    )


def test_research_artifact_serializer_serializes_lineage():

    serializer = ResearchArtifactSerializer()

    artifact = serializer.serialize(
        specification=build_specification(),
        cycle=FakeCycle(),
        lineage=build_lineage(),
    )

    assert (
        artifact["lineage"]["parent_artifact_id"]
        == "artifact-000"
    )

    assert (
        artifact["lineage"]["lineage_type"]
        == "derived_from"
    )

    assert (
        artifact["lineage"]["change_description"]
        == "Added ADX confirmation feature"
    )

    assert (
        artifact["lineage"]["created_from_experiment"]
        == "experiment-002"
    )