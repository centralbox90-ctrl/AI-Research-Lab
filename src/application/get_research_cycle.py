from src.application.research_cycle_repository import (
    ResearchCycleRepository,
)
from src.research import NextExperimentResearchCycleResult


class GetResearchCycle:
    """
    Application use case for retrieving a completed research cycle.
    """

    def __init__(
        self,
        repository: ResearchCycleRepository,
    ) -> None:
        self.repository = repository

    def execute(
        self,
        result_id: str,
    ) -> NextExperimentResearchCycleResult | None:
        return self.repository.get(result_id)