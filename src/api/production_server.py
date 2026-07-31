from __future__ import annotations

import argparse
from ipaddress import ip_address
from collections.abc import Sequence
from pathlib import Path

from waitress import serve

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
    Run the HTTP API through the production WSGI server.

    TLS termination, authentication and external network
    exposure remain deployment responsibilities.
    """

    parser = argparse.ArgumentParser(
        prog=(
            "python -m "
            "src.api.production_server"
        ),
        description=(
            "Run the AI Research Lab HTTP API "
            "through Waitress."
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
            "Loopback interface to bind. "
            "Defaults to 127.0.0.1."
        ),
    )
    parser.add_argument(
        "--port",
        type=_parse_port,
        default=8080,
        help=(
            "TCP port. Defaults to 8080."
        ),
    )
    parser.add_argument(
        "--threads",
        type=_parse_threads,
        default=4,
        help=(
            "Number of Waitress worker threads. "
            "Defaults to 4."
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

    serve(
        application,
        host=arguments.host,
        port=arguments.port,
        threads=arguments.threads,
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


def _parse_threads(value: str) -> int:
    try:
        threads = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            "threads must be an integer"
        ) from error

    if threads < 1:
        raise argparse.ArgumentTypeError(
            "threads must be positive"
        )

    return threads


if __name__ == "__main__":
    raise SystemExit(main())
