from pathlib import Path

from .diff_engine import DiffEngine
from .replay import ReplayEngine, SnapshotInfo


class ChangeReportEngine:

    SEPARATOR = "=" * 70

    def __init__(self):

        self.replay = ReplayEngine()
        self.diff_engine = DiffEngine()

    def read_snapshot(
        self,
        snapshot: SnapshotInfo,
    ) -> str:

        return snapshot.snapshot_path.read_text(
            encoding="utf-8",
        )

    def build_latest_report(
        self,
        file_path: str,
    ) -> str:

        target = Path(file_path)

        snapshots = self.replay.get_snapshots_for_file(
            str(target)
        )

        if len(snapshots) < 2:

            return (
                f"{self.SEPARATOR}\n"
                f"File: {target}\n"
                f"Snapshots: {len(snapshots)}\n"
                f"{self.SEPARATOR}\n"
                "Not enough snapshots for report."
            )

        old_snapshot = snapshots[-2]
        new_snapshot = snapshots[-1]

        old_content = self.read_snapshot(
            old_snapshot
        )

        new_content = self.read_snapshot(
            new_snapshot
        )

        diff = self.diff_engine.compare_snapshots(
            old_snapshot,
            new_snapshot,
        )

        if not diff:
            diff = "No text changes detected."

        sections = [
            self.SEPARATOR,
            "PROJECT MEMORY — CHANGE REPORT",
            self.SEPARATOR,
            f"FILE: {target}",
            f"OLD DATE: {old_snapshot.timestamp.isoformat(sep=' ')}",
            f"NEW DATE: {new_snapshot.timestamp.isoformat(sep=' ')}",
            f"SNAPSHOTS: {len(snapshots)}",
            self.SEPARATOR,
            "BEFORE — FULL OLD CODE",
            self.SEPARATOR,
            old_content,
            self.SEPARATOR,
            "AFTER — FULL NEW CODE",
            self.SEPARATOR,
            new_content,
            self.SEPARATOR,
            "DIFF — EXACT CHANGES",
            self.SEPARATOR,
            diff,
            self.SEPARATOR,
        ]

        return "\n".join(sections)


def main() -> None:

    file_path = "src/research/question.py"

    report_engine = ChangeReportEngine()

    report = report_engine.build_latest_report(
        file_path
    )

    print(report)


if __name__ == "__main__":
    main()