from src.application import GetSerializedResearchCycle
from src.cli.research_cycle_json import ResearchCycleJsonPresenter


class GetResearchCycleCommand:
    """
    CLI command handler for retrieving a saved research cycle as JSON.

    The handler does not parse process arguments and does not access
    repositories directly. It coordinates application and presentation
    boundaries only.
    """

    def __init__(
        self,
        get_serialized_research_cycle: GetSerializedResearchCycle,
        presenter: ResearchCycleJsonPresenter | None = None,
    ) -> None:
        self.get_serialized_research_cycle = (
            get_serialized_research_cycle
        )
        self.presenter = presenter or ResearchCycleJsonPresenter()

    def execute(
        self,
        result_id: str,
        *,
        indent: int | None = 2,
    ) -> str | None:
        serialized_cycle = self.get_serialized_research_cycle.execute(
            result_id
        )

        if serialized_cycle is None:
            return None

        return self.presenter.render(
            serialized_cycle,
            indent=indent,
        )