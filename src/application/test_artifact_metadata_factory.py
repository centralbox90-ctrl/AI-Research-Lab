from src.application.artifact_metadata_factory import ArtifactMetadataFactory


def test_artifact_metadata_factory_creation():

    factory = ArtifactMetadataFactory()

    metadata = factory.create(
        experiment_id="experiment-001",
        executor_type="market_backtest_executor",
        executor_version="1.0",
        data_source="BTCUSDT_1H",
        code_version="abc123",
    )

    assert metadata.artifact_id is not None
    assert metadata.schema_version == "1.0"
    assert metadata.experiment_id == "experiment-001"
    assert metadata.executor_type == "market_backtest_executor"
    assert metadata.executor_version == "1.0"
    assert metadata.data_source == "BTCUSDT_1H"
    assert metadata.code_version == "abc123"