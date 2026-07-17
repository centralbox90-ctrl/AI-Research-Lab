from pathlib import Path

from .diff_engine import DiffEngine
from .replay import ReplayEngine, SnapshotInfo


class ChangeHistoryEngine:

    SEPARATOR = "=" * 70
    SUBSEPARATOR = "-" * 70

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

    def build_file_history(
        self,
        file_path: str,
    ) -> str:

        target = Path(file_path)

        snapshots = self.replay.get_snapshots_for_file(
            str(target)
        )

        if not snapshots:

            return (
                f"{self.SEPARATOR}\n"
                f"FILE: {target}\n"
                f"{self.SEPARATOR}\n"
                "No snapshots found."
            )

        sections = [
            self.SEPARATOR,
            "PROJECT MEMORY — FULL FILE HISTORY",
            self.SEPARATOR,
            f"FILE: {target}",
            f"TOTAL SNAPSHOTS: {len(snapshots)}",
            f"TOTAL CHANGES: {max(0, len(snapshots) - 1)}",
            self.SEPARATOR,
        ]

        if len(snapshots) == 1:

            snapshot = snapshots[0]

            sections.extend(
                [
                    "INITIAL VERSION",
                    f"DATE: {snapshot.timestamp.isoformat(sep=' ')}",
                    self.SUBSEPARATOR,
                    self.read_snapshot(snapshot),
                    self.SEPARATOR,
                ]
            )

            return "\n".join(sections)

        for change_number, (
            old_snapshot,
            new_snapshot,
        ) in enumerate(
            zip(snapshots, snapshots[1:]),
            start=1,
        ):

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

            sections.extend(
                [
                    f"CHANGE #{change_number}",
                    f"FILE: {target}",
                    (
                        "OLD DATE: "
                        f"{old_snapshot.timestamp.isoformat(sep=' ')}"
                    ),
                    (
                        "NEW DATE: "
                        f"{new_snapshot.timestamp.isoformat(sep=' ')}"
                    ),
                    self.SUBSEPARATOR,
                    "BEFORE — FULL OLD CODE",
                    self.SUBSEPARATOR,
                    old_content,
                    self.SUBSEPARATOR,
                    "AFTER — FULL NEW CODE",
                    self.SUBSEPARATOR,
                    new_content,
                    self.SUBSEPARATOR,
                    "DIFF — EXACT CHANGES",
                    self.SUBSEPARATOR,
                    diff,
                    self.SEPARATOR,
                ]
            )

        return "\n".join(sections)


def main() -> None:

    file_path = "src/research/question.py"

    history_engine = ChangeHistoryEngine()

    history = history_engine.build_file_history(
        file_path
    )

    print(history)


if __name__ == "__main__":
    main()