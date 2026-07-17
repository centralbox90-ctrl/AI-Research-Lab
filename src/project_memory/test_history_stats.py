from datetime import date

from .history_stats import HistoryStatsEngine


class FakeHistoryEngine:

    def __init__(self) -> None:

        self.journal = {
            date(2026, 7, 13): {
                "src/example.py": [
                    {
                        "event_type": "CREATED",
                    },
                    {
                        "event_type": "MODIFIED",
                    },
                    {
                        "event_type": "MODIFIED",
                    },
                ],
                "src/other.py": [
                    {
                        "event_type": "DELETED",
                    },
                    {
                        "event_type": "MOVED",
                    },
                ],
            }
        }

    def build_grouped_journal(self):

        return self.journal


def create_stats_engine() -> HistoryStatsEngine:

    stats = HistoryStatsEngine()

    stats.history = FakeHistoryEngine()

    return stats


def test_history_stats() -> None:

    stats = create_stats_engine()

    result = stats.build_daily_stats(
        date(2026, 7, 13)
    )

    assert "13.07.2026" in result
    assert "TOTAL EVENTS: 5" in result
    assert "FILES CHANGED: 2" in result
    assert "CREATED: 1" in result
    assert "MODIFIED: 2" in result
    assert "DELETED: 1" in result
    assert "MOVED: 1" in result
    assert "src/example.py" in result
    assert "EVENTS: 3" in result


def test_history_stats_empty_day() -> None:

    stats = create_stats_engine()

    result = stats.build_daily_stats(
        date(2026, 1, 1)
    )

    assert result == (
        "No history found for selected date."
    )