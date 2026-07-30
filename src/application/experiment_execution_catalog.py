from typing import Protocol


class ExperimentExecutionCatalog(Protocol):
    """Application port for discovering persisted executions."""

    def list_execution_ids(
        self,
    ) -> tuple[str, ...]:
        """Return persisted execution identities."""
