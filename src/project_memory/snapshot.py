import shutil
import time
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from .config import SNAPSHOT_DIR


class SnapshotEngine:

    WAIT_TIMEOUT = 5.0
    CHECK_INTERVAL = 0.1

    def __init__(
        self,
        snapshot_dir: str | Path = SNAPSHOT_DIR,
        project_root: str | Path | None = None,
    ):

        self.snapshot_dir = Path(snapshot_dir)

        self.project_root = (
            Path(project_root).resolve()
            if project_root is not None
            else Path.cwd().resolve()
        )

        self.snapshot_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def wait_until_available(
        self,
        path: Path,
    ) -> bool:

        start = time.time()

        while time.time() - start < self.WAIT_TIMEOUT:

            try:

                with path.open("rb"):
                    return True

            except (PermissionError, OSError):

                time.sleep(self.CHECK_INTERVAL)

        return False

    def create_snapshot(
        self,
        file_path: str,
    ) -> Path | None:

        source = Path(file_path).resolve()

        if not source.exists() or not source.is_file():
            return None

        if not self.wait_until_available(source):

            print(
                f"[WARNING] File is locked: {source}"
            )

            return None

        now = datetime.now()

        snapshot_id = (
            f"{now:%Y%m%d_%H%M%S_%f}_"
            f"{uuid4().hex[:8]}"
        )

        try:

            relative_source = source.relative_to(
                self.project_root
            )

        except ValueError:

            relative_source = Path(source.name)

        destination = (
            self.snapshot_dir
            / snapshot_id
            / relative_source
        )

        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.copy2(
            source,
            destination,
        )

        print(f"[SNAPSHOT] {destination}")

        return destination