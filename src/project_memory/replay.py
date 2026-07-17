from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .config import SNAPSHOT_DIR


@dataclass(slots=True)
class SnapshotInfo:

    timestamp: datetime
    original_path: Path
    snapshot_path: Path


class ReplayEngine:

    def __init__(self):

        self.snapshot_dir = SNAPSHOT_DIR

    def _parse_new_snapshot(
        self,
        file: Path,
        parts: tuple[str, ...],
    ) -> SnapshotInfo | None:

        if len(parts) < 2:
            return None

        snapshot_id = parts[0]

        try:

            timestamp_text = "_".join(
                snapshot_id.split("_")[:3]
            )

            timestamp = datetime.strptime(
                timestamp_text,
                "%Y%m%d_%H%M%S_%f",
            )

        except ValueError:
            return None

        original_path = Path(*parts[1:])

        return SnapshotInfo(
            timestamp=timestamp,
            original_path=original_path,
            snapshot_path=file,
        )

    def _parse_legacy_snapshot(
        self,
        file: Path,
        parts: tuple[str, ...],
    ) -> SnapshotInfo | None:

        if len(parts) < 7:
            return None

        try:

            year, month, day, hour, minute, second = map(
                int,
                parts[:6],
            )

            timestamp = datetime(
                year,
                month,
                day,
                hour,
                minute,
                second,
            )

        except ValueError:
            return None

        original_path = Path(*parts[6:])

        return SnapshotInfo(
            timestamp=timestamp,
            original_path=original_path,
            snapshot_path=file,
        )

    def list_snapshots(self) -> list[SnapshotInfo]:

        snapshots: list[SnapshotInfo] = []

        if not self.snapshot_dir.exists():
            return snapshots

        for file in self.snapshot_dir.rglob("*"):

            if not file.is_file():
                continue

            relative = file.relative_to(
                self.snapshot_dir
            )

            parts = relative.parts

            snapshot = self._parse_new_snapshot(
                file,
                parts,
            )

            if snapshot is None:

                snapshot = self._parse_legacy_snapshot(
                    file,
                    parts,
                )

            if snapshot is not None:
                snapshots.append(snapshot)

        snapshots.sort(
            key=lambda snapshot: snapshot.timestamp
        )

        return snapshots

    def get_snapshots_for_file(
        self,
        file_path: str,
    ) -> list[SnapshotInfo]:

        target = Path(file_path)

        return [
            snapshot
            for snapshot in self.list_snapshots()
            if snapshot.original_path == target
        ]