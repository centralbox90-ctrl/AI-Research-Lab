from pathlib import Path

from .replay import SnapshotInfo


class RestoreEngine:

    def read_snapshot(self, snapshot: SnapshotInfo) -> str:

        path = Path(snapshot.snapshot_path)

        return path.read_text(
            encoding="utf-8"
        )