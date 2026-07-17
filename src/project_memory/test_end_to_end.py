import sqlite3
from pathlib import Path

from .database import ProjectDatabase
from .diff_engine import DiffEngine
from .event import EventType
from .replay import ReplayEngine
from .restore import RestoreEngine
from .snapshot import SnapshotEngine
from .watcher import ProjectWatcher


def test_project_memory_end_to_end(
    tmp_path: Path,
) -> None:

    project_root = tmp_path / "project"

    source_file = (
        project_root
        / "src"
        / "example.py"
    )

    source_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    memory_dir = (
        project_root
        / ".project_memory"
    )

    database_path = (
        memory_dir
        / "events.db"
    )

    snapshot_dir = (
        memory_dir
        / "snapshots"
    )

    database = ProjectDatabase(
        database_path
    )

    snapshot_engine = SnapshotEngine(
        snapshot_dir=snapshot_dir,
        project_root=project_root,
    )

    watcher = ProjectWatcher(
        database=database,
        snapshot_engine=snapshot_engine,
    )

    source_file.write_text(
        "value = 1\n",
        encoding="utf-8",
    )

    watcher.handle_event(
        EventType.CREATED,
        str(source_file),
    )

    watcher._last_event_time.clear()

    watcher.handle_event(
        EventType.MODIFIED,
        str(source_file),
    )

    source_file.write_text(
        "value = 2\n",
        encoding="utf-8",
    )

    watcher._last_event_time.clear()

    watcher.handle_event(
        EventType.MODIFIED,
        str(source_file),
    )

    connection = sqlite3.connect(
        database_path
    )

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT event_type
        FROM events
        ORDER BY timestamp
        """
    )

    event_types = [
        row[0]
        for row in cursor.fetchall()
    ]

    connection.close()

    assert event_types == [
        "CREATED",
        "MODIFIED",
        "MODIFIED",
    ]

    replay = ReplayEngine()

    replay.snapshot_dir = snapshot_dir

    snapshots = replay.get_snapshots_for_file(
        "src/example.py"
    )

    assert len(snapshots) == 2

    restore = RestoreEngine()

    old_text = restore.read_snapshot(
        snapshots[0]
    )

    new_text = restore.read_snapshot(
        snapshots[1]
    )

    assert old_text == "value = 1\n"
    assert new_text == "value = 2\n"

    diff = DiffEngine().compare_snapshots(
        snapshots[0],
        snapshots[1],
    )

    assert "-value = 1" in diff
    assert "+value = 2" in diff