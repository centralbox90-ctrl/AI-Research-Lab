from src.application.artifact_metadata import ArtifactMetadata
from src.application.ports.clock import Clock
from src.application.ports.id_generator import IdGenerator
from src.application.system_clock import SystemClock
from src.application.uuid_id_generator import UuidIdGenerator


class ArtifactMetadataFactory:

    def __init__(
        self,
        clock: Clock | None = None,
        id_generator: IdGenerator | None = None,
    ) -> None:
        self._clock = clock or SystemClock()
        self._id_generator = id_generator or UuidIdGenerator()

    def create(
        self,
        experiment_id: str | None,
        executor_type: str | None,
        executor_version: str | None,
        data_source: str | None,
        code_version: str | None,
    ) -> ArtifactMetadata:

        return ArtifactMetadata(
            artifact_id=self._id_generator.generate(),
            schema_version="1.0",
            created_at=self._clock.now(),
            experiment_id=experiment_id,
            executor_type=executor_type,
            executor_version=executor_version,
            data_source=data_source,
            code_version=code_version,
        )
