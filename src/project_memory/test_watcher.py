from pathlib import Path
from types import SimpleNamespace

from .event import EventType
from .watcher import ProjectWatcher


class FakeDatabase:

    def __init__(self) -> None:

        self.events = []

    def save_event(self, event) -> None:

        self.events.append(event)


class FakeSnapshotEngine:

    def __init__(self) -> None:

        self.paths = []

    def create_snapshot(
        self,
        file_path: str,
    ) -> Path:

        self.paths.append(file_path)

        return Path(file_path)


def create_watcher() -> tuple[
    ProjectWatcher,
    FakeDatabase,
    FakeSnapshotEngine,
]:

    database = FakeDatabase()

    snapshot_engine = FakeSnapshotEngine()

    watcher = ProjectWatcher(
        database=database,
        snapshot_engine=snapshot_engine,
    )

    return (
        watcher,
        database,
        snapshot_engine,
    )


def test_should_ignore_project_memory() -> None:

    watcher, _, _ = create_watcher()

    assert watcher.should_ignore(
        ".project_memory/events.db"
    )


def test_should_ignore_python_cache() -> None:

    watcher, _, _ = create_watcher()

    assert watcher.should_ignore(
        "src/__pycache__/module.pyc"
    )


def test_should_ignore_extension() -> None:

    watcher, _, _ = create_watcher()

    assert watcher.should_ignore(
        "logs/project.log"
    )


def test_should_not_ignore_python_file() -> None:

    watcher, _, _ = create_watcher()

    assert not watcher.should_ignore(
        "src/example.py"
    )


def test_duplicate_event_detection() -> None:

    watcher, _, _ = create_watcher()

    assert not watcher.is_duplicate_event(
        "src/example.py"
    )

    assert watcher.is_duplicate_event(
        "src/example.py"
    )


def test_created_event_is_saved() -> None:

    watcher, database, snapshot_engine = (
        create_watcher()
    )

    watcher.on_created(
        SimpleNamespace(
            is_directory=False,
            src_path="src/example.py",
        )
    )

    assert len(database.events) == 1
    assert database.events[0].event_type is (
        EventType.CREATED
    )
    assert snapshot_engine.paths == []


def test_directory_event_is_ignored() -> None:

    watcher, database, snapshot_engine = (
        create_watcher()
    )

    watcher.on_created(
        SimpleNamespace(
            is_directory=True,
            src_path="src/example",
        )
    )

    assert database.events == []
    assert snapshot_engine.paths == []


def test_modified_event_creates_snapshot(
    tmp_path: Path,
) -> None:

    watcher, database, snapshot_engine = (
        create_watcher()
    )

    file_path = tmp_path / "example.py"

    file_path.write_text(
        "value = 1\n",
        encoding="utf-8",
    )

    watcher.on_modified(
        SimpleNamespace(
            is_directory=False,
            src_path=str(file_path),
        )
    )

    assert len(database.events) == 1
    assert database.events[0].event_type is (
        EventType.MODIFIED
    )
    assert snapshot_engine.paths == [
        str(file_path)
    ]


def test_deleted_event_does_not_create_snapshot() -> None:

    watcher, database, snapshot_engine = (
        create_watcher()
    )

    watcher.on_deleted(
        SimpleNamespace(
            is_directory=False,
            src_path="src/example.py",
        )
    )

    assert len(database.events) == 1
    assert database.events[0].event_type is (
        EventType.DELETED
    )
    assert snapshot_engine.paths == []


def test_moved_event_uses_destination_path() -> None:

    watcher, database, snapshot_engine = (
        create_watcher()
    )

    watcher.on_moved(
        SimpleNamespace(
            is_directory=False,
            src_path="src/old.py",
            dest_path="src/new.py",
        )
    )

    assert len(database.events) == 1
    assert database.events[0].event_type is (
        EventType.MOVED
    )
    assert database.events[0].file_path == str(
        Path("src/new.py")
    )
    assert snapshot_engine.paths == []