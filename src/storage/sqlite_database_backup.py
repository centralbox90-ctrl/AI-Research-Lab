from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path
from uuid import uuid4


class SqliteBackupError(RuntimeError):
    """
    Raised when SQLite backup integrity cannot be guaranteed.
    """


class SqliteDatabaseBackup:
    """
    Create, verify and restore complete SQLite databases.

    Existing destination files are never intentionally replaced.
    Restore therefore requires an absent destination path.
    """

    def create(
        self,
        *,
        database_path: str | Path,
        backup_path: str | Path,
    ) -> Path:
        return self._copy_database(
            source_path=database_path,
            destination_path=backup_path,
        )

    def verify(
        self,
        *,
        backup_path: str | Path,
    ) -> bool:
        path = Path(backup_path)

        try:
            self._verify_database(path)
        except SqliteBackupError:
            raise
        except (OSError, sqlite3.Error) as error:
            raise SqliteBackupError(
                "SQLite backup integrity validation failed."
            ) from error

        return True

    def restore(
        self,
        *,
        backup_path: str | Path,
        database_path: str | Path,
    ) -> Path:
        self.verify(
            backup_path=backup_path,
        )

        return self._copy_database(
            source_path=backup_path,
            destination_path=database_path,
        )

    def _copy_database(
        self,
        *,
        source_path: str | Path,
        destination_path: str | Path,
    ) -> Path:
        source = Path(source_path)
        destination = Path(destination_path)

        if source.resolve() == destination.resolve():
            raise ValueError(
                "SQLite source and destination paths "
                "must be different."
            )

        if not source.is_file():
            raise FileNotFoundError(
                f"SQLite source database does not exist: "
                f"{source}"
            )

        if destination.exists():
            raise FileExistsError(
                f"SQLite destination already exists: "
                f"{destination}"
            )

        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        temporary_path = destination.with_name(
            (
                f".{destination.name}."
                f"{uuid4().hex}.tmp"
            )
        )

        try:
            with closing(
                self._open_read_only(source)
            ) as source_connection:
                with closing(
                    sqlite3.connect(
                        temporary_path
                    )
                ) as destination_connection:
                    source_connection.backup(
                        destination_connection
                    )
                    destination_connection.commit()

            self._verify_database(
                temporary_path
            )

            if destination.exists():
                raise FileExistsError(
                    f"SQLite destination already exists: "
                    f"{destination}"
                )

            temporary_path.replace(
                destination
            )
        except SqliteBackupError:
            self._discard_temporary_file(
                temporary_path
            )
            raise
        except (OSError, sqlite3.Error) as error:
            self._discard_temporary_file(
                temporary_path
            )
            raise SqliteBackupError(
                "SQLite database copy failed."
            ) from error

        return destination

    def _verify_database(
        self,
        path: Path,
    ) -> None:
        if not path.is_file():
            raise SqliteBackupError(
                "SQLite backup file does not exist."
            )

        with closing(
            self._open_read_only(path)
        ) as connection:
            rows = connection.execute(
                "PRAGMA integrity_check"
            ).fetchall()

        if rows != [("ok",)]:
            raise SqliteBackupError(
                "SQLite backup integrity validation failed."
            )

    @staticmethod
    def _discard_temporary_file(
        path: Path,
    ) -> None:
        try:
            path.unlink(
                missing_ok=True
            )
        except OSError:
            return

    @staticmethod
    def _open_read_only(
        path: Path,
    ) -> sqlite3.Connection:
        database_uri = (
            path.resolve().as_uri()
            + "?mode=ro"
        )

        return sqlite3.connect(
            database_uri,
            uri=True,
        )
