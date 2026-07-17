from datetime import datetime
from pathlib import Path

from .change_history import ChangeHistoryEngine


class HistoryExportEngine:

    def __init__(
        self,
        export_dir: str = ".project_memory/reports",
    ):

        self.export_dir = Path(export_dir)

        self.export_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.history_engine = ChangeHistoryEngine()

    def export_file_history(
        self,
        file_path: str,
    ) -> Path:

        report = self.history_engine.build_file_history(
            file_path
        )

        target = Path(file_path)

        safe_name = "_".join(target.parts)

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S_%f"
        )

        report_path = (
            self.export_dir
            / f"{safe_name}_{timestamp}.txt"
        )

        report_path.write_text(
            report,
            encoding="utf-8",
        )

        return report_path


def main() -> None:

    file_path = "src/research/question.py"

    exporter = HistoryExportEngine()

    report_path = exporter.export_file_history(
        file_path
    )

    print("=" * 70)
    print("PROJECT MEMORY — HISTORY EXPORTED")
    print("=" * 70)
    print(f"File: {file_path}")
    print(f"Report: {report_path.resolve()}")
    print("=" * 70)


if __name__ == "__main__":
    main()