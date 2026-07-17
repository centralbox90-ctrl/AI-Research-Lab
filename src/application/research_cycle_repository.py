from typing import Protocol

from src.research import NextExperimentResearchCycleResult


class ResearchCycleRepository(Protocol):
    """
    Persistence boundary for completed research cycles.

    Implementations may store cycles in memory, a database, or another
    storage system without adding persistence responsibilities to the
    research core.
    """

    def save(
        self,
        cycle: NextExperimentResearchCycleResult,
    ) -> None:
        """
        Save a completed research cycle.
        """

    def get(
        self,
        result_id: str,
    ) -> NextExperimentResearchCycleResult | None:
        """
        Return a completed research cycle by experiment result ID.
        """