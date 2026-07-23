from __future__ import annotations

import json
from argparse import (
    ArgumentParser,
    ArgumentTypeError,
)
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from src.application.compare_indicator_comparative_research_artifacts import (
    CompareIndicatorComparativeResearchArtifacts,
)
from src.application.indicator_comparative_research_artifact_loader import (
    IndicatorComparativeResearchArtifactLoader,
)
from src.application.research_artifact_file_exporter import (
    ResearchArtifactFileExporter,
)


def build_argument_parser() -> ArgumentParser:
    parser = ArgumentParser(
        description=(
            "Compare two saved comparative "
            "indicator research artifacts."
        )
    )
    parser.add_argument(
        "artifact_a_path",
        type=Path,
    )
    parser.add_argument(
        "artifact_b_path",
        type=Path,
    )
    parser.add_argument(
        "--output",
        type=Path,
    )
    parser.add_argument(
        "--indent",
        default=2,
        type=_parse_nonnegative_integer,
    )

    return parser


def compare_artifacts(
    *,
    artifact_a_path: Path,
    artifact_b_path: Path,
) -> dict[str, Any]:
    loader = (
        IndicatorComparativeResearchArtifactLoader()
    )
    artifact_a = loader.load(
        artifact_a_path
    )
    artifact_b = loader.load(
        artifact_b_path
    )

    return (
        CompareIndicatorComparativeResearchArtifacts()
        .execute(
            artifact_a,
            artifact_b,
        )
    )


def main(
    arguments: Sequence[str] | None = None,
) -> int:
    parser = build_argument_parser()
    parsed = parser.parse_args(arguments)

    try:
        comparison = compare_artifacts(
            artifact_a_path=(
                parsed.artifact_a_path
            ),
            artifact_b_path=(
                parsed.artifact_b_path
            ),
        )
    except (TypeError, ValueError) as error:
        parser.error(str(error))

    if parsed.output is not None:
        ResearchArtifactFileExporter().export(
            comparison,
            parsed.output,
        )

    print(
        json.dumps(
            comparison,
            indent=parsed.indent,
            sort_keys=True,
            ensure_ascii=False,
            allow_nan=False,
        )
    )

    return 0


def _parse_nonnegative_integer(
    value: str,
) -> int:
    try:
        parsed = int(value)
    except ValueError as error:
        raise ArgumentTypeError(
            "value must be an integer"
        ) from error

    if parsed < 0:
        raise ArgumentTypeError(
            "value must not be negative"
        )

    return parsed


if __name__ == "__main__":
    raise SystemExit(main())
