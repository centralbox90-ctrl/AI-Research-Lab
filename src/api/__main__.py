from __future__ import annotations

import argparse
from ipaddress import ip_address
from collections.abc import Sequence
from pathlib import Path

from src.api.composition_root import (
    build_research_api,
)
from src.storage import (
    RESEARCH_CYCLE_DATABASE_PATH,
)


def main(
    argv: Sequence[str] | None = None,
) -> int:
    """
    Run the local HTTP development server.

    Production deployment must use a dedicated
    WSGI server and separate security configuration.
    """

    parser = argparse.ArgumentParser(
        prog="python -m src.api",
        description=(
            "Run the local AI Research Lab "
            "HTTP API."
        ),
    )
    parser.add_argument(
        "--database",
        type=Path,
        default=RESEARCH_CYCLE_DATABASE_PATH,
        help=(
            "Path to the SQLite research "
            "database."
        ),
    )
    parser.add_argument(
        "--host",
        type=_parse_host,
        default="127.0.0.1",
        help=(
            "Local loopback interface to bind. "
            "Defaults to 127.0.0.1."
        ),
    )
    parser.add_argument(
        "--port",
        type=_parse_port,
        default=8000,
        help=(
            "Local TCP port. "
            "Defaults to 8000."
        ),
    )

    arguments = parser.parse_args(
        None
        if argv is None
        else list(argv)
    )

    application = build_research_api(
        db_path=arguments.database,
    )

    application.run(
        host=arguments.host,
        port=arguments.port,
        debug=False,
        use_reloader=False,
    )

    return 0


def _parse_host(value: str) -> str:
    normalized = value.strip()

    if not normalized:
        raise argparse.ArgumentTypeError(
            "host must not be empty"
        )

    if normalized.casefold() == "localhost":
        return "localhost"

    try:
        address = ip_address(normalized)
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            "host must be localhost or "
            "a loopback IP address"
        ) from error

    if not address.is_loopback:
        raise argparse.ArgumentTypeError(
            "host must be localhost or "
            "a loopback IP address"
        )

    return normalized


def _parse_port(value: str) -> int:
    try:
        port = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            "port must be an integer"
        ) from error

    if port < 1 or port > 65535:
        raise argparse.ArgumentTypeError(
            "port must be between 1 and 65535"
        )

    return port


if __name__ == "__main__":
    raise SystemExit(main())