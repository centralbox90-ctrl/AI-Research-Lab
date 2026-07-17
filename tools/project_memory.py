import sys

from src.project_memory.history import HistoryEngine


def show_history():

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


def main():

    if len(sys.argv) < 2:

        print("Usage:")

        print("python tools/project_memory.py history")

        return

    command = sys.argv[1].lower()

    if command == "history":

        show_history()

    else:

        print(f"Unknown command: {command}")


if __name__ == "__main__":

    main()