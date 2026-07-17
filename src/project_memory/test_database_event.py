import sqlite3
from datetime import datetime
from pathlib import Path
from uuid import UUID

from .database import ProjectDatabase
from .event import EventType
from .event import ProjectEvent


def test_project_event_create() -> None:

    event = ProjectEvent.create(
        EventType.CREATED,
        "src/example.py",
    )

    UUID(event.id)

    assert event.event_type is EventType.CREATED
    assert event.file_path == str(
        Path("src/example.py")
    )
    assert isinstance(event.timestamp, datetime)
    assert event.is_directory is False


def test_project_event_create_directory() -> None:

    event = ProjectEvent.create(
        EventType.CREATED,
        "src/example",
        is_directory=True,
    )

    assert event.is_directory is True


def test_database_creates_events_table(
    tmp_path: Path,
) -> None:

    database_path = (
        tmp_path
        / "database"
        / "events.db"
    )

    ProjectDatabase(database_path)

    assert database_path.exists()

    connection = sqlite3.connect(
        database_path
    )

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        AND name = 'events'
        """
    )

    table = cursor.fetchone()

    connection.close()

    assert table == ("events",)


def test_database_saves_event(
    tmp_path: Path,
) -> None:

    database_path = tmp_path / "events.db"

    database = ProjectDatabase(
        database_path
    )

    event = ProjectEvent.create(
        EventType.MODIFIED,
        "src/example.py",
    )

    database.save_event(event)

    connection = sqlite3.connect(
        database_path
    )

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            timestamp,
            event_type,
            file_path,
            is_directory
        FROM events
        WHERE id = ?
        """,
        (event.id,),
    )

    row = cursor.fetchone()

    connection.close()

    assert row is not None
    assert row[0] == event.id
    assert row[1] == event.timestamp.isoformat()
    assert row[2] == "MODIFIED"
    assert row[3] == str(
        Path("src/example.py")
    )
    assert row[4] == 0


def test_database_saves_directory_event(
    tmp_path: Path,
) -> None:

    database_path = tmp_path / "events.db"

    database = ProjectDatabase(
        database_path
    )

    event = ProjectEvent.create(
        EventType.CREATED,
        "src/example",
        is_directory=True,
    )

    database.save_event(event)

    connection = sqlite3.connect(
        database_path
    )

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT is_directory
        FROM events
        WHERE id = ?
        """,
        (event.id,),
    )

    row = cursor.fetchone()

    connection.close()

    assert row == (1,)