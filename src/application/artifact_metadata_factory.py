from uuid import uuid4

from src.application.artifact_metadata import ArtifactMetadata
from src.application.ports.clock import Clock
from src.application.system_clock import SystemClock


class ArtifactMetadataFactory:

    def __init__(self, clock: Clock | None = None) -> None:
        self._clock = clock or SystemClock()

    def create(
        self,
        experiment_id: str | None,
        executor_type: str | None,
        executor_version: str | None,
        data_source: str | None,
        code_version: str | None,
    ) -> ArtifactMetadata:

        return ArtifactMetadata(
            artifact_id=str(uuid4()),
            schema_version="1.0",
            created_at=self._clock.now(),
            experiment_id=experiment_id,
            executor_type=executor_type,
            executor_version=executor_version,
            data_source=data_source,
            code_version=code_version,
        )
