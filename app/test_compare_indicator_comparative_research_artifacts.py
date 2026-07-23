import json
from pathlib import Path
from typing import Any

import pytest

from app import (
    compare_indicator_comparative_research_artifacts
    as comparison_cli,
)


def build_artifact(
    *,
    research_fingerprint: str,
    dataset_id: str,
    symbol: str = "EURUSD",
    metric_shift: float = 0.0,
) -> dict[str, Any]:
    return {
        "artifact_type": (
            "indicator_comparative_research"
        ),
        "artifact_version": 1,
        "indicator": {
            "id": "rsi",
            "research_fingerprint": (
                research_fingerprint
            ),
        },
        "market": {
            "symbol": symbol,
            "timeframe": "H1",
        },
        "dataset": {
            "id": dataset_id,
        },
        "outcome_specification": {
            "horizons": [1],
            "price_field": "close",
        },
        "analysis": {
            "comparisons": [
                {
                    "horizon": 1,
                    "mean_return_difference": (
                        0.01 + metric_shift
                    ),
                    "median_return_difference": (
                        0.02 + metric_shift
                    ),
                    "positive_rate_difference": (
                        0.03 + metric_shift
                    ),
                },
            ],
        },
    }


def write_artifact(
    path: Path,
    artifact: dict[str, Any],
) -> None:
    path.write_text(
        json.dumps(artifact),
        encoding="utf-8",
    )


def build_artifact_files(
    tmp_path: Path,
) -> tuple[Path, Path]:
    artifact_a_path = (
        tmp_path / "artifact-a.json"
    )
    artifact_b_path = (
        tmp_path / "artifact-b.json"
    )

    write_artifact(
        artifact_a_path,
        build_artifact(
            research_fingerprint="research-a",
            dataset_id="dataset-a",
        ),
    )
    write_artifact(
        artifact_b_path,
        build_artifact(
            research_fingerprint="research-b",
            dataset_id="dataset-b",
            metric_shift=0.05,
        ),
    )

    return (
        artifact_a_path,
        artifact_b_path,
    )


def test_parses_default_arguments() -> None:
    parsed = (
        comparison_cli.build_argument_parser()
        .parse_args(
            [
                "artifact-a.json",
                "artifact-b.json",
            ]
        )
    )

    assert parsed.artifact_a_path == Path(
        "artifact-a.json"
    )
    assert parsed.artifact_b_path == Path(
        "artifact-b.json"
    )
    assert parsed.output is None
    assert parsed.indent == 2


def test_parses_output_and_indent() -> None:
    parsed = (
        comparison_cli.build_argument_parser()
        .parse_args(
            [
                "artifact-a.json",
                "artifact-b.json",
                "--output",
                "comparison.json",
                "--indent",
                "0",
            ]
        )
    )

    assert parsed.output == Path(
        "comparison.json"
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
            comparison_cli.build_argument_parser()
            .parse_args(
                [
                    "artifact-a.json",
                    "artifact-b.json",
                    "--indent",
                    value,
                ]
            )
        )


def test_compares_loaded_artifacts(
    tmp_path: Path,
) -> None:
    (
        artifact_a_path,
        artifact_b_path,
    ) = build_artifact_files(tmp_path)

    comparison = (
        comparison_cli.compare_artifacts(
            artifact_a_path=artifact_a_path,
            artifact_b_path=artifact_b_path,
        )
    )

    assert comparison["artifact_a"] == {
        "research_fingerprint": "research-a",
        "dataset_id": "dataset-a",
    }
    assert comparison["artifact_b"] == {
        "research_fingerprint": "research-b",
        "dataset_id": "dataset-b",
    }

    horizon_deltas = comparison[
        "horizon_deltas"
    ]

    assert isinstance(horizon_deltas, list)
    assert horizon_deltas[0][
        "mean_return_difference_delta"
    ] == pytest.approx(0.05)


def test_main_prints_and_exports_comparison(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    (
        artifact_a_path,
        artifact_b_path,
    ) = build_artifact_files(tmp_path)
    output_path = (
        tmp_path
        / "nested"
        / "comparison.json"
    )

    exit_code = comparison_cli.main(
        [
            str(artifact_a_path),
            str(artifact_b_path),
            "--output",
            str(output_path),
        ]
    )
    printed = json.loads(
        capsys.readouterr().out
    )
    exported = json.loads(
        output_path.read_text(
            encoding="utf-8",
        )
    )

    assert exit_code == 0
    assert printed == exported
    assert printed["artifact_type"] == (
        "indicator_comparative_research_comparison"
    )
    assert list(
        output_path.parent.glob(
            ".comparison.json.*.tmp"
        )
    ) == []


def test_main_rejects_incompatible_artifacts(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    (
        artifact_a_path,
        artifact_b_path,
    ) = build_artifact_files(tmp_path)
    artifact_b = json.loads(
        artifact_b_path.read_text(
            encoding="utf-8",
        )
    )
    artifact_b["market"]["symbol"] = "GBPUSD"
    write_artifact(
        artifact_b_path,
        artifact_b,
    )

    with pytest.raises(
        SystemExit,
        match="2",
    ):
        comparison_cli.main(
            [
                str(artifact_a_path),
                str(artifact_b_path),
            ]
        )

    error_output = capsys.readouterr().err

    assert "same symbol" in error_output
