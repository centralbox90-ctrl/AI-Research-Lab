from collections import Counter
from datetime import date

from .history import HistoryEngine


class HistoryStatsEngine:

    SEPARATOR = "=" * 70

    def __init__(self):

        self.history = HistoryEngine()

    def build_daily_stats(
        self,
        target_day: date | None = None,
    ) -> str:

        journal = self.history.build_grouped_journal()

        if not journal:
            return "Project history is empty."

        days = (
            [target_day]
            if target_day is not None
            else sorted(journal)
        )

        sections = []

        for day in days:

            files = journal.get(day)

            if not files:
                continue

            event_types = Counter()

            file_event_counts = {}

            total_events = 0

            for file_path, events in files.items():

                file_event_counts[file_path] = len(
                    events
                )

                total_events += len(events)

                for event in events:

                    event_types[
                        event["event_type"]
                    ] += 1

            most_changed_file = max(
                file_event_counts,
                key=file_event_counts.get,
            )

            sections.extend(
                [
                    self.SEPARATOR,
                    day.strftime("%d.%m.%Y"),
                    self.SEPARATOR,
                    f"TOTAL EVENTS: {total_events}",
                    f"FILES CHANGED: {len(files)}",
                    (
                        "CREATED: "
                        f"{event_types.get('CREATED', 0)}"
                    ),
                    (
                        "MODIFIED: "
                        f"{event_types.get('MODIFIED', 0)}"
                    ),
                    (
                        "DELETED: "
                        f"{event_types.get('DELETED', 0)}"
                    ),
                    (
                        "MOVED: "
                        f"{event_types.get('MOVED', 0)}"
                    ),
                    "",
                    "MOST CHANGED FILE:",
                    most_changed_file,
                    (
                        "EVENTS: "
                        f"{file_event_counts[most_changed_file]}"
                    ),
                ]
            )

        if not sections:
            return "No history found for selected date."

        sections.append(self.SEPARATOR)

        return "\n".join(sections)


def main() -> None:

    stats = HistoryStatsEngine()

    print(
        stats.build_daily_stats()
    )


if __name__ == "__main__":
    main()