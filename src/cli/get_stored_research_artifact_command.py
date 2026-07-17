from src.application import GetStoredResearchArtifact
from src.cli.research_cycle_json import ResearchCycleJsonPresenter


class GetStoredResearchArtifactCommand:
    """
    CLI command handler for retrieving persistent research artifacts.

    The handler receives application-safe dictionaries from the
    application layer and renders them as JSON.
    """

    def __init__(
        self,
        get_stored_research_artifact: GetStoredResearchArtifact,
        presenter: ResearchCycleJsonPresenter | None = None,
    ) -> None:
        self.get_stored_research_artifact = (
            get_stored_research_artifact
        )

        self.presenter = (
            presenter
            or ResearchCycleJsonPresenter()
        )

    def execute(
        self,
        result_id: str,
        *,
        indent: int | None = 2,
    ) -> str | None:
        stored_artifact = (
            self.get_stored_research_artifact.execute(
                result_id,
            )
        )

        if stored_artifact is None:
            return None

        return self.presenter.render(
            stored_artifact,
            indent=indent,
        )