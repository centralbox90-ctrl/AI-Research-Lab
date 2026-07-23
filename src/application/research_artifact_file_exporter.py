from __future__ import annotations

import json
from pathlib import Path
from tempfile import NamedTemporaryFile
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

        serialized = (
            json.dumps(
                artifact,
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
                allow_nan=False,
            )
            + "\n"
        )

        temporary_path: Path | None = None

        try:
            with NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                newline="\n",
                dir=output_path.parent,
                prefix=f".{output_path.name}.",
                suffix=".tmp",
                delete=False,
            ) as temporary_file:
                temporary_path = Path(
                    temporary_file.name
                )
                temporary_file.write(
                    serialized
                )

            temporary_path.replace(
                output_path
            )
        except BaseException:
            if temporary_path is not None:
                temporary_path.unlink(
                    missing_ok=True
                )

            raise

        return output_path
