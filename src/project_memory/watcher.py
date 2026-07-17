import time
from pathlib import Path

from watchdog.events import FileSystemEventHandler

from .config import (
    IGNORED_DIRECTORIES,
    IGNORED_EXTENSIONS,
)
from .database import ProjectDatabase
from .event import EventType, ProjectEvent
from .snapshot import SnapshotEngine


class ProjectWatcher(FileSystemEventHandler):

    EVENT_DEBOUNCE_SECONDS = 1.0

    def __init__(
        self,
        database: ProjectDatabase | None = None,
        snapshot_engine: SnapshotEngine | None = None,
    ):

        super().__init__()

        self.database = (
            database
            if database is not None
            else ProjectDatabase()
        )

        self.snapshot_engine = (
            snapshot_engine
            if snapshot_engine is not None
            else SnapshotEngine()
        )

        self._last_event_time: dict[str, float] = {}

    def should_ignore(
        self,
        file_path: str,
    ) -> bool:

        path = Path(file_path)

        for part in path.parts:

            if part in IGNORED_DIRECTORIES:
                return True

        if path.suffix.lower() in IGNORED_EXTENSIONS:
            return True

        return False

    def is_duplicate_event(
        self,
        file_path: str,
    ) -> bool:

        normalized_path = str(
            Path(file_path).resolve()
        ).lower()

        current_time = time.monotonic()

        previous_time = self._last_event_time.get(
            normalized_path
        )

        if (
            previous_time is not None
            and current_time - previous_time
            < self.EVENT_DEBOUNCE_SECONDS
        ):
            return True

        self._last_event_time[
            normalized_path
        ] = current_time

        return False

    def handle_event(
        self,
        event_type: EventType,
        file_path: str,
    ) -> None:

        if self.should_ignore(file_path):
            return

        if self.is_duplicate_event(file_path):
            return

        project_event = ProjectEvent.create(
            event_type=event_type,
            path=file_path,
            is_directory=False,
        )

        self.database.save_event(
            project_event
        )

        if event_type == EventType.MODIFIED:

            source = Path(file_path)

            if source.exists() and source.is_file():

                self.snapshot_engine.create_snapshot(
                    file_path
                )

        print(
            f"[{event_type.value}] {file_path}"
        )

    def on_created(
        self,
        event,
    ) -> None:

        if event.is_directory:
            return

        self.handle_event(
            EventType.CREATED,
            event.src_path,
        )

    def on_modified(
        self,
        event,
    ) -> None:

        if event.is_directory:
            return

        self.handle_event(
            EventType.MODIFIED,
            event.src_path,
        )

    def on_deleted(
        self,
        event,
    ) -> None:

        if event.is_directory:
            return

        self.handle_event(
            EventType.DELETED,
            event.src_path,
        )

    def on_moved(
        self,
        event,
    ) -> None:

        if event.is_directory:
            return

        destination_path = getattr(
            event,
            "dest_path",
            event.src_path,
        )

        self.handle_event(
            EventType.MOVED,
            destination_path,
        )