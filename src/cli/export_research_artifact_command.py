from pathlib import Path

from src.application import (
    ExportStoredResearchArtifact,
)


class ExportResearchArtifactCommand:
    """
    CLI command for exporting stored research artifacts.

    The command delegates artifact retrieval and file creation
    to the application layer.
    """

    def __init__(
        self,
        export_stored_research_artifact: (
            ExportStoredResearchArtifact
        ),
    ) -> None:
        self.export_stored_research_artifact = (
            export_stored_research_artifact
        )

    def execute(
        self,
        result_id: str,
        output_path: str | Path,
    ) -> str | None:
        exported_path = (
            self.export_stored_research_artifact.execute(
                result_id=result_id,
                output_path=output_path,
            )
        )

        if exported_path is None:
            return None

        return str(exported_path)