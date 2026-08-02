import json
from pathlib import Path

from src.storage import (
    SqliteResearchCycleStore,
)
from src.storage.sqlite_backup_cli import (
    main,
)


def test_creates_verifies_and_restores_backup(
    tmp_path: Path,
    capsys,
) -> None:
    database_path = tmp_path / "research.db"
    backup_path = tmp_path / "backup.db"
    restored_path = tmp_path / "restored.db"
    artifact = {
        "result": {
            "id": "result-001",
        },
    }
    SqliteResearchCycleStore(
        db_path=database_path,
    ).save(
        result_id="result-001",
        serialized_cycle=artifact,
    )

    create_exit_code = main(
        [
            "create",
            "--database",
            str(database_path),
            "--backup",
            str(backup_path),
        ]
    )
    create_output = json.loads(
        capsys.readouterr().out
    )

    assert create_exit_code == 0
    assert create_output == {
        "schema_version": 1,
        "operation": "create",
        "status": "created",
        "backup_path": str(backup_path),
    }

    verify_exit_code = main(
        [
            "verify",
            "--backup",
            str(backup_path),
        ]
    )
    verify_output = json.loads(
        capsys.readouterr().out
    )

    assert verify_exit_code == 0
    assert verify_output == {
        "schema_version": 1,
        "operation": "verify",
        "status": "valid",
        "backup_path": str(backup_path),
    }

    restore_exit_code = main(
        [
            "restore",
            "--backup",
            str(backup_path),
            "--database",
            str(restored_path),
        ]
    )
    restore_output = json.loads(
        capsys.readouterr().out
    )

    assert restore_exit_code == 0
    assert restore_output == {
        "schema_version": 1,
        "operation": "restore",
        "status": "restored",
        "database_path": str(restored_path),
    }
    assert SqliteResearchCycleStore(
        db_path=restored_path,
    ).get("result-001") == artifact


def test_create_reports_missing_source(
    tmp_path: Path,
    capsys,
) -> None:
    exit_code = main(
        [
            "create",
            "--database",
            str(tmp_path / "missing.db"),
            "--backup",
            str(tmp_path / "backup.db"),
        ]
    )
    captured = capsys.readouterr()
    error = json.loads(captured.err)

    assert exit_code == 1
    assert captured.out == ""
    assert error["schema_version"] == 1
    assert error["error"]["code"] == (
        "sqlite_backup_operation_failed"
    )
    assert (
        "source database does not exist"
        in error["error"]["message"]
    )


def test_verify_reports_corrupted_backup(
    tmp_path: Path,
    capsys,
) -> None:
    backup_path = tmp_path / "corrupted.db"
    backup_path.write_bytes(
        b"not-a-sqlite-database"
    )

    exit_code = main(
        [
            "verify",
            "--backup",
            str(backup_path),
        ]
    )
    captured = capsys.readouterr()
    error = json.loads(captured.err)

    assert exit_code == 1
    assert captured.out == ""
    assert error["error"]["code"] == (
        "sqlite_backup_operation_failed"
    )
    assert (
        "integrity validation failed"
        in error["error"]["message"]
    )


def test_restore_refuses_existing_database(
    tmp_path: Path,
    capsys,
) -> None:
    source_path = tmp_path / "source.db"
    backup_path = tmp_path / "backup.db"
    database_path = tmp_path / "database.db"
    SqliteResearchCycleStore(
        db_path=source_path,
    )
    assert main(
        [
            "create",
            "--database",
            str(source_path),
            "--backup",
            str(backup_path),
        ]
    ) == 0
    capsys.readouterr()
    database_path.write_bytes(
        b"existing-database"
    )

    exit_code = main(
        [
            "restore",
            "--backup",
            str(backup_path),
            "--database",
            str(database_path),
        ]
    )
    captured = capsys.readouterr()
    error = json.loads(captured.err)

    assert exit_code == 1
    assert captured.out == ""
    assert error["error"]["code"] == (
        "sqlite_backup_operation_failed"
    )
    assert (
        "destination already exists"
        in error["error"]["message"]
    )
    assert database_path.read_bytes() == (
        b"existing-database"
    )
