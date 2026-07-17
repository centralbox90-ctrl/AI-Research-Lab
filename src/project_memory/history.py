from collections import defaultdict
from datetime import datetime
from pathlib import Path

from .database import ProjectDatabase


class HistoryEngine:

    def __init__(self):

        self.database = ProjectDatabase()

    def get_all_events(self) -> list[dict]:

        connection = self.database.get_connection()

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                timestamp,
                event_type,
                file_path
            FROM events
            ORDER BY timestamp ASC
            """
        )

        rows = cursor.fetchall()

        connection.close()

        events = []

        for timestamp, event_type, file_path in rows:

            events.append(
                {
                    "timestamp": datetime.fromisoformat(
                        timestamp
                    ),
                    "event_type": event_type.upper(),
                    "path": Path(file_path),
                }
            )

        return events

    def build_journal(self) -> dict:

        events = self.get_all_events()

        journal = defaultdict(list)

        for event in events:

            day = event["timestamp"].date()

            journal[day].append(event)

        return dict(journal)

    def build_grouped_journal(self) -> dict:

        events = self.get_all_events()

        journal = defaultdict(
            lambda: defaultdict(list)
        )

        for event in events:

            day = event["timestamp"].date()

            file_path = str(event["path"])

            journal[day][file_path].append(
                event
            )

        return {
            day: dict(files)
            for day, files in journal.items()
        }

    def format_grouped_journal(self) -> str:

        journal = self.build_grouped_journal()

        if not journal:
            return "Project history is empty."

        lines = []

        for day in sorted(journal):

            lines.append("=" * 70)

            lines.append(
                day.strftime("%d.%m.%Y")
            )

            lines.append("=" * 70)

            files = journal[day]

            for file_path in sorted(files):

                events = files[file_path]

                lines.append("")
                lines.append(f"FILE: {file_path}")
                lines.append("-" * 70)

                for event in events:

                    event_time = (
                        event["timestamp"]
                        .strftime("%H:%M:%S.%f")
                    )

                    lines.append(
                        f"{event_time}  "
                        f"{event['event_type']}"
                    )

                lines.append(
                    f"TOTAL EVENTS: {len(events)}"
                )

        lines.append("=" * 70)

        return "\n".join(lines)