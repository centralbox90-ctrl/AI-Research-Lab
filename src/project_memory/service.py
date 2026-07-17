import time
from pathlib import Path

from watchdog.observers import Observer

from .watcher import ProjectWatcher


class ProjectMemoryService:

    def __init__(self) -> None:

        self.project_path = Path(".").resolve()

        self.observer = Observer()

    def start(self) -> None:

        print("=" * 60)
        print("Project Memory Engine")
        print("=" * 60)
        print(f"Watching: {self.project_path}")
        print("=" * 60)

        watcher = ProjectWatcher()

        self.observer.schedule(
            watcher,
            str(self.project_path),
            recursive=True,
        )

        self.observer.start()

        try:

            while True:
                time.sleep(1)

        except KeyboardInterrupt:

            print(
                "\nStopping Project Memory Engine..."
            )

            self.observer.stop()

        self.observer.join()


def main() -> None:

    service = ProjectMemoryService()

    service.start()


if __name__ == "__main__":
    main()