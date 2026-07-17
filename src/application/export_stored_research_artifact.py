from pathlib import Path

from src.application.get_stored_research_artifact import (
    GetStoredResearchArtifact,
)
from src.application.research_artifact_file_exporter import (
    ResearchArtifactFileExporter,
)


class ExportStoredResearchArtifact:
    """
    Exports a stored research artifact into a JSON file.

    Storage retrieval and filesystem writing are separated.
    """

    def __init__(
        self,
        get_stored_research_artifact: GetStoredResearchArtifact,
        exporter: ResearchArtifactFileExporter | None = None,
    ) -> None:
        self.get_stored_research_artifact = (
            get_stored_research_artifact
        )

        self.exporter = (
            exporter
            or ResearchArtifactFileExporter()
        )

    def execute(
        self,
        result_id: str,
        output_path: str | Path,
    ) -> Path | None:
        artifact = (
            self.get_stored_research_artifact.execute(
                result_id,
            )
        )

        if artifact is None:
            return None

        return self.exporter.export(
            artifact,
            output_path,
        )