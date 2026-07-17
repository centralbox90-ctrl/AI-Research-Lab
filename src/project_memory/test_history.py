from src.project_memory.history import HistoryEngine

history = HistoryEngine()

journal = history.build_journal()

for day in sorted(journal):

    print("=" * 70)

    print(day)

    print("=" * 70)

    for event in journal[day]:

        print(
            f"{event['timestamp'].strftime('%H:%M:%S')}  "
            f"{event['event_type']:<10}  "
            f"{event['path'].name}"
        )

    print()