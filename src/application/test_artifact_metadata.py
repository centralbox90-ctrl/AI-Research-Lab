from datetime import datetime

from src.application.artifact_metadata import ArtifactMetadata


def test_artifact_metadata_creation():

    metadata = ArtifactMetadata(
        artifact_id="artifact-001",
        schema_version="1.0",
        created_at=datetime(2026, 7, 14, 21, 0, 0),
        experiment_id="experiment-001",
        executor_type="market_backtest_executor",
        executor_version="1.0",
        data_source="BTCUSDT_1H",
        code_version=None,
    )

    assert metadata.artifact_id == "artifact-001"
    assert metadata.schema_version == "1.0"
    assert metadata.experiment_id == "experiment-001"
    assert metadata.data_source == "BTCUSDT_1H"