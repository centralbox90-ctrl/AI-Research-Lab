import json
from pathlib import Path
from typing import Any


class ResearchArtifactFileExporter:
    """
    Writes serialized research artifacts to JSON files.

    The exporter only handles filesystem output.
    It does not load artifacts and does not access storage.
    """

    def export(
        self,
        artifact: dict[str, Any],
        path: str | Path,
    ) -> Path:
        output_path = Path(path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_path.write_text(
            json.dumps(
                artifact,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        return output_path