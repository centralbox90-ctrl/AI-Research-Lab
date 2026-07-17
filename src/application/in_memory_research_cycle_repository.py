from src.research import NextExperimentResearchCycleResult


class InMemoryResearchCycleRepository:
    """
    In-memory storage for completed research cycles.

    Cycles are indexed by ExperimentResult.id. This implementation is
    intended for application tests and local execution before a database
    adapter is introduced.
    """

    def __init__(self) -> None:
        self._cycles: dict[str, NextExperimentResearchCycleResult] = {}

    def save(
        self,
        cycle: NextExperimentResearchCycleResult,
    ) -> None:
        self._cycles[cycle.result.id] = cycle

    def get(
        self,
        result_id: str,
    ) -> NextExperimentResearchCycleResult | None:
        return self._cycles.get(result_id)