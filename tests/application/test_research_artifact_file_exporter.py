import json
from pathlib import Path

import pytest

from src.application.research_artifact_file_exporter import (
    ResearchArtifactFileExporter,
)


def test_exports_deterministic_json(
    tmp_path: Path,
) -> None:
    output_path = (
        tmp_path
        / "nested"
        / "artifact.json"
    )
    artifact = {
        "zeta": 2,
        "alpha": {
            "beta": True,
        },
    }

    exported_path = (
        ResearchArtifactFileExporter().export(
            artifact,
            output_path,
        )
    )

    assert exported_path == output_path
    assert output_path.read_text(
        encoding="utf-8",
    ) == (
        "{\n"
        '  "alpha": {\n'
        '    "beta": true\n'
        "  },\n"
        '  "zeta": 2\n'
        "}\n"
    )
    assert json.loads(
        output_path.read_text(
            encoding="utf-8",
        )
    ) == artifact
    assert list(
        output_path.parent.glob(
            ".artifact.json.*.tmp"
        )
    ) == []


def test_replaces_existing_artifact(
    tmp_path: Path,
) -> None:
    output_path = tmp_path / "artifact.json"
    output_path.write_text(
        "old artifact",
        encoding="utf-8",
    )

    ResearchArtifactFileExporter().export(
        {"version": 2},
        output_path,
    )

    assert json.loads(
        output_path.read_text(
            encoding="utf-8",
        )
    ) == {
        "version": 2,
    }


def test_rejects_non_finite_numbers_without_overwrite(
    tmp_path: Path,
) -> None:
    output_path = tmp_path / "artifact.json"
    output_path.write_text(
        "stable artifact",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="Out of range float values",
    ):
        ResearchArtifactFileExporter().export(
            {
                "metric": float("nan"),
            },
            output_path,
        )

    assert output_path.read_text(
        encoding="utf-8",
    ) == "stable artifact"
    assert list(
        tmp_path.glob(
            ".artifact.json.*.tmp"
        )
    ) == []


def test_removes_temporary_file_when_replace_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_path = tmp_path / "artifact.json"
    output_path.write_text(
        "stable artifact",
        encoding="utf-8",
    )

    def reject_replace(
        temporary_path: Path,
        target: Path,
    ) -> Path:
        assert target == output_path
        raise OSError(
            "replace failed"
        )

    monkeypatch.setattr(
        Path,
        "replace",
        reject_replace,
    )

    with pytest.raises(
        OSError,
        match="replace failed",
    ):
        ResearchArtifactFileExporter().export(
            {"version": 2},
            output_path,
        )

    assert output_path.read_text(
        encoding="utf-8",
    ) == "stable artifact"
    assert list(
        tmp_path.glob(
            ".artifact.json.*.tmp"
        )
    ) == []
