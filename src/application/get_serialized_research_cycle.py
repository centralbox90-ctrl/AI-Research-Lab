from typing import Any

from src.application.research_cycle_repository import (
    ResearchCycleRepository,
)
from src.application.research_cycle_serializer import (
    ResearchCycleSerializer,
)


class GetSerializedResearchCycle:
    """
    Application use case for retrieving and serializing a research cycle.

    This use case provides framework-independent data suitable for
    presentation by CLI, HTTP API, or another external adapter.
    """

    def __init__(
        self,
        repository: ResearchCycleRepository,
        serializer: ResearchCycleSerializer | None = None,
    ) -> None:
        self.repository = repository
        self.serializer = serializer or ResearchCycleSerializer()

    def execute(
        self,
        result_id: str,
    ) -> dict[str, Any] | None:
        cycle = self.repository.get(result_id)

        if cycle is None:
            return None

        return self.serializer.serialize(cycle)