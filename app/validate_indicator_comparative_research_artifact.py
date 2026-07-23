from __future__ import annotations

import json
from argparse import (
    ArgumentParser,
    ArgumentTypeError,
)
from collections.abc import Sequence
from pathlib import Path

from src.application.indicator_comparative_research_artifact_loader import (
    IndicatorComparativeResearchArtifactLoader,
)


def build_argument_parser() -> ArgumentParser:
    parser = ArgumentParser(
        description=(
            "Validate a saved comparative "
            "indicator research artifact."
        )
    )
    parser.add_argument(
        "artifact_path",
        type=Path,
    )
    parser.add_argument(
        "--indent",
        default=2,
        type=_parse_nonnegative_integer,
    )

    return parser


def main(
    arguments: Sequence[str] | None = None,
) -> int:
    parser = build_argument_parser()
    parsed = parser.parse_args(arguments)

    try:
        artifact = (
            IndicatorComparativeResearchArtifactLoader()
            .load(parsed.artifact_path)
        )
    except ValueError as error:
        parser.error(str(error))

    print(
        json.dumps(
            {
                "valid": True,
                "path": str(parsed.artifact_path),
                "artifact_type": artifact[
                    "artifact_type"
                ],
                "artifact_version": artifact[
                    "artifact_version"
                ],
            },
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
