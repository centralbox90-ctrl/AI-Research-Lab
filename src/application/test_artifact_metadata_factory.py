from datetime import UTC, datetime

from src.application.artifact_metadata_factory import ArtifactMetadataFactory


class StubClock:

    def __init__(self, current_time: datetime) -> None:
        self._current_time = current_time

    def now(self) -> datetime:
        return self._current_time


class StubIdGenerator:

    def __init__(self, generated_id: str) -> None:
        self._generated_id = generated_id

    def generate(self) -> str:
        return self._generated_id


def test_artifact_metadata_factory_creation():

    created_at = datetime(2026, 7, 17, 12, 30, tzinfo=UTC)
    artifact_id = "artifact-001"

    factory = ArtifactMetadataFactory(
        clock=StubClock(created_at),
        id_generator=StubIdGenerator(artifact_id),
    )

    metadata = factory.create(
        experiment_id="experiment-001",
        executor_type="market_backtest_executor",
        executor_version="1.0",
        data_source="BTCUSDT_1H",
        code_version="abc123",
    )

    assert metadata.artifact_id == artifact_id
    assert metadata.schema_version == "1.0"
    assert metadata.created_at == created_at
    assert metadata.experiment_id == "experiment-001"
    assert metadata.executor_type == "market_backtest_executor"
    assert metadata.executor_version == "1.0"
    assert metadata.data_source == "BTCUSDT_1H"
    assert metadata.code_version == "abc123"
