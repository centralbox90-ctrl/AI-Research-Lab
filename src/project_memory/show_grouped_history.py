from src.project_memory.history import HistoryEngine


def main() -> None:

    history = HistoryEngine()

    print(
        history.format_grouped_journal()
    )


if __name__ == "__main__":
    main()