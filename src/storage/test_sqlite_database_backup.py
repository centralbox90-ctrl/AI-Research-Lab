from pathlib import Path

import pytest

from src.storage import (
    SqliteBackupError,
    SqliteDatabaseBackup,
    SqliteResearchCycleStore,
)


def test_creates_verifies_and_restores_sqlite_database(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "research.db"
    backup_path = (
        tmp_path / "backups" / "research.db"
    )
    restored_path = tmp_path / "restored.db"
    store = SqliteResearchCycleStore(
        db_path=database_path,
    )
    artifact = {
        "result": {
            "id": "result-001",
        },
    }
    store.save(
        result_id="result-001",
        serialized_cycle=artifact,
    )
    service = SqliteDatabaseBackup()

    created_path = service.create(
        database_path=database_path,
        backup_path=backup_path,
    )

    assert created_path == backup_path
    assert service.verify(
        backup_path=backup_path,
    ) is True
    assert SqliteResearchCycleStore(
        db_path=backup_path,
    ).get("result-001") == artifact

    restored_result = service.restore(
        backup_path=backup_path,
        database_path=restored_path,
    )

    assert restored_result == restored_path
    assert SqliteResearchCycleStore(
        db_path=restored_path,
    ).get("result-001") == artifact


def test_rejects_missing_backup_source(
    tmp_path: Path,
) -> None:
    service = SqliteDatabaseBackup()
    backup_path = tmp_path / "backup.db"

    with pytest.raises(
        FileNotFoundError,
        match="source database does not exist",
    ):
        service.create(
            database_path=tmp_path / "missing.db",
            backup_path=backup_path,
        )

    assert backup_path.exists() is False


def test_refuses_to_replace_existing_backup(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "research.db"
    backup_path = tmp_path / "backup.db"
    SqliteResearchCycleStore(
        db_path=database_path,
    )
    backup_path.write_bytes(
        b"existing-backup"
    )
    service = SqliteDatabaseBackup()

    with pytest.raises(
        FileExistsError,
        match="destination already exists",
    ):
        service.create(
            database_path=database_path,
            backup_path=backup_path,
        )

    assert backup_path.read_bytes() == (
        b"existing-backup"
    )


def test_rejects_same_source_and_destination(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "research.db"
    SqliteResearchCycleStore(
        db_path=database_path,
    )

    with pytest.raises(
        ValueError,
        match="paths must be different",
    ):
        SqliteDatabaseBackup().create(
            database_path=database_path,
            backup_path=database_path,
        )


def test_rejects_corrupted_sqlite_backup(
    tmp_path: Path,
) -> None:
    backup_path = tmp_path / "corrupted.db"
    backup_path.write_bytes(
        b"not-a-sqlite-database"
    )

    with pytest.raises(
        SqliteBackupError,
        match="integrity validation failed",
    ):
        SqliteDatabaseBackup().verify(
            backup_path=backup_path,
        )


def test_restore_refuses_existing_database(
    tmp_path: Path,
) -> None:
    source_path = tmp_path / "source.db"
    backup_path = tmp_path / "backup.db"
    database_path = tmp_path / "database.db"
    SqliteResearchCycleStore(
        db_path=source_path,
    )
    service = SqliteDatabaseBackup()
    service.create(
        database_path=source_path,
        backup_path=backup_path,
    )
    database_path.write_bytes(
        b"existing-database"
    )

    with pytest.raises(
        FileExistsError,
        match="destination already exists",
    ):
        service.restore(
            backup_path=backup_path,
            database_path=database_path,
        )

    assert database_path.read_bytes() == (
        b"existing-database"
    )
