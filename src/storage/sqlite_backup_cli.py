from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import TextIO

from src.storage.sqlite_database_backup import (
    SqliteBackupError,
    SqliteDatabaseBackup,
)


def main(
    argv: Sequence[str] | None = None,
) -> int:
    parser = argparse.ArgumentParser(
        prog=(
            "python -m "
            "src.storage.sqlite_backup_cli"
        ),
        description=(
            "Create, verify or restore an "
            "AI Research Lab SQLite backup."
        ),
    )
    subparsers = parser.add_subparsers(
        dest="operation",
        required=True,
    )

    create_parser = subparsers.add_parser(
        "create",
        help=(
            "Create an integrity-validated "
            "SQLite backup."
        ),
    )
    create_parser.add_argument(
        "--database",
        type=Path,
        required=True,
        help="Source SQLite database.",
    )
    create_parser.add_argument(
        "--backup",
        type=Path,
        required=True,
        help=(
            "New backup path. Existing files "
            "are never replaced."
        ),
    )

    verify_parser = subparsers.add_parser(
        "verify",
        help=(
            "Run SQLite integrity validation "
            "for a backup."
        ),
    )
    verify_parser.add_argument(
        "--backup",
        type=Path,
        required=True,
        help="Existing SQLite backup.",
    )

    restore_parser = subparsers.add_parser(
        "restore",
        help=(
            "Restore a backup into a new "
            "database path."
        ),
    )
    restore_parser.add_argument(
        "--backup",
        type=Path,
        required=True,
        help="Existing SQLite backup.",
    )
    restore_parser.add_argument(
        "--database",
        type=Path,
        required=True,
        help=(
            "New database path. Existing files "
            "are never replaced."
        ),
    )

    arguments = parser.parse_args(
        None
        if argv is None
        else list(argv)
    )
    service = SqliteDatabaseBackup()

    try:
        if arguments.operation == "create":
            result_path = service.create(
                database_path=arguments.database,
                backup_path=arguments.backup,
            )
            result = {
                "schema_version": 1,
                "operation": "create",
                "status": "created",
                "backup_path": str(result_path),
            }
        elif arguments.operation == "verify":
            service.verify(
                backup_path=arguments.backup,
            )
            result = {
                "schema_version": 1,
                "operation": "verify",
                "status": "valid",
                "backup_path": str(
                    arguments.backup
                ),
            }
        else:
            result_path = service.restore(
                backup_path=arguments.backup,
                database_path=arguments.database,
            )
            result = {
                "schema_version": 1,
                "operation": "restore",
                "status": "restored",
                "database_path": str(result_path),
            }
    except (
        FileExistsError,
        FileNotFoundError,
        SqliteBackupError,
        ValueError,
    ) as error:
        _write_json(
            sys.stderr,
            {
                "schema_version": 1,
                "error": {
                    "code": (
                        "sqlite_backup_"
                        "operation_failed"
                    ),
                    "message": str(error),
                },
            },
        )
        return 1

    _write_json(
        sys.stdout,
        result,
    )

    return 0


def _write_json(
    stream: TextIO,
    payload: dict[str, object],
) -> None:
    stream.write(
        json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n"
    )


if __name__ == "__main__":
    raise SystemExit(main())
