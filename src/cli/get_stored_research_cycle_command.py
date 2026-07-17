from src.application import GetStoredResearchCycle
from src.cli.research_cycle_json import ResearchCycleJsonPresenter


class GetStoredResearchCycleCommand:
    """
    CLI command handler for retrieving persistent research-cycle data.

    The handler receives application-safe dictionaries from the
    application layer and renders them as JSON.
    """

    def __init__(
        self,
        get_stored_research_cycle: GetStoredResearchCycle,
        presenter: ResearchCycleJsonPresenter | None = None,
    ) -> None:
        self.get_stored_research_cycle = get_stored_research_cycle
        self.presenter = presenter or ResearchCycleJsonPresenter()

    def execute(
        self,
        result_id: str,
        *,
        indent: int | None = 2,
    ) -> str | None:
        stored_cycle = self.get_stored_research_cycle.execute(
            result_id
        )

        if stored_cycle is None:
            return None

        return self.presenter.render(
            stored_cycle,
            indent=indent,
        )