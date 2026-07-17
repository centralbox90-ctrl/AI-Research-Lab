import json

from src.application import ListStoredResearchCycles


class ListStoredResearchCyclesCommand:
    """
    CLI command handler for listing persistent research-cycle IDs.
    """

    def __init__(
        self,
        list_stored_research_cycles: ListStoredResearchCycles,
    ) -> None:
        self.list_stored_research_cycles = list_stored_research_cycles

    def execute(
        self,
        *,
        indent: int | None = 2,
    ) -> str:
        result_ids = self.list_stored_research_cycles.execute()

        return json.dumps(
            result_ids,
            ensure_ascii=False,
            indent=indent,
            sort_keys=True,
        )