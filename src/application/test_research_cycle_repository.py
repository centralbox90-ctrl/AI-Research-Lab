from src.application.research_cycle_repository import (
    ResearchCycleRepository,
)
from src.research import NextExperimentResearchCycleResult


class RepositoryImplementation:
    def save(
        self,
        cycle: NextExperimentResearchCycleResult,
    ) -> None:
        pass

    def get(
        self,
        result_id: str,
    ) -> NextExperimentResearchCycleResult | None:
        return None


def test_research_cycle_repository_defines_application_boundary() -> None:
    repository: ResearchCycleRepository = RepositoryImplementation()

    assert repository.get("missing-result") is None