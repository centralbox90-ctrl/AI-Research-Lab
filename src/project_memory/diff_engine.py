import difflib
from pathlib import Path

from .replay import SnapshotInfo


class DiffEngine:

    def compare_text(
        self,
        old_text: str,
        new_text: str,
    ) -> str:

        diff = difflib.unified_diff(
            old_text.splitlines(),
            new_text.splitlines(),
            fromfile="OLD",
            tofile="NEW",
            lineterm="",
        )

        return "\n".join(diff)

    def compare_files(
        self,
        old_file: Path,
        new_file: Path,
    ) -> str:

        old_text = old_file.read_text(
            encoding="utf-8"
        )

        new_text = new_file.read_text(
            encoding="utf-8"
        )

        return self.compare_text(
            old_text,
            new_text,
        )

    def compare_snapshots(
        self,
        old_snapshot: SnapshotInfo,
        new_snapshot: SnapshotInfo,
    ) -> str:

        return self.compare_files(
            old_snapshot.snapshot_path,
            new_snapshot.snapshot_path,
        )