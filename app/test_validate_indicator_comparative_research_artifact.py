import json
from pathlib import Path

import pytest

from app import (
    validate_indicator_comparative_research_artifact
    as validator,
)


def build_artifact() -> dict[str, object]:
    return {
        "artifact_type": (
            "indicator_comparative_research"
        ),
        "artifact_version": 1,
        "indicator": {
            "id": "rsi",
        },
        "market": {
            "symbol": "EURUSD",
            "timeframe": "H1",
        },
        "dataset": {
            "id": "dataset-id",
        },
        "outcome_specification": {
            "horizons": [1, 3, 5],
        },
        "analysis": {
            "comparisons": [],
        },
    }


def write_artifact(
    path: Path,
    artifact: dict[str, object],
) -> None:
    path.write_text(
        json.dumps(artifact),
        encoding="utf-8",
    )


def test_parses_default_arguments() -> None:
    parsed = validator.build_argument_parser().parse_args(
        [
            "result.json",
        ]
    )

    assert parsed.artifact_path == Path(
        "result.json"
    )
    assert parsed.indent == 2


def test_parses_custom_indent() -> None:
    parsed = validator.build_argument_parser().parse_args(
        [
            "result.json",
            "--indent",
            "0",
        ]
    )

    assert parsed.indent == 0


@pytest.mark.parametrize(
    "value",
    [
        "-1",
        "invalid",
    ],
)
def test_rejects_invalid_indent(
    value: str,
) -> None:
    with pytest.raises(
        SystemExit,
        match="2",
    ):
        (
            validator.build_argument_parser()
            .parse_args(
                [
                    "result.json",
                    "--indent",
                    value,
                ]
            )
        )


def test_main_validates_artifact(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    artifact_path = tmp_path / "result.json"
    write_artifact(
        artifact_path,
        build_artifact(),
    )

    exit_code = validator.main(
        [
            str(artifact_path),
        ]
    )
    output = json.loads(
        capsys.readouterr().out
    )

    assert exit_code == 0
    assert output == {
        "valid": True,
        "path": str(artifact_path),
        "artifact_type": (
            "indicator_comparative_research"
        ),
        "artifact_version": 1,
    }


def test_main_rejects_invalid_artifact(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    artifact_path = tmp_path / "invalid.json"
    artifact = build_artifact()
    artifact["artifact_type"] = "other"
    write_artifact(
        artifact_path,
        artifact,
    )

    with pytest.raises(
        SystemExit,
        match="2",
    ):
        validator.main(
            [
                str(artifact_path),
            ]
        )

    error_output = capsys.readouterr().err

    assert "artifact_type must be" in error_output
