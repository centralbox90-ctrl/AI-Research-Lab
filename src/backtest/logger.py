from datetime import datetime


class EventLogger:
    """
    Журнал событий торговой системы.
    """

    def __init__(self):

        self.events = []

    def log(self, event_type, message, **kwargs):

        event = {
            "time": datetime.now(),
            "type": event_type,
            "message": message,
            "data": kwargs
        }

        self.events.append(event)

    def print(self):

        print("\n========== EVENT LOG ==========\n")

        for event in self.events:

            print(
                f"[{event['time']:%Y-%m-%d %H:%M:%S}] "
                f"{event['type']}"
            )

            print(event["message"])

            if event["data"]:

                for key, value in event["data"].items():
                    print(f"   {key}: {value}")

            print()

        print("===============================\n")

    def to_dataframe(self):

        import pandas as pd

        rows = []

        for event in self.events:

            row = {
                "time": event["time"],
                "type": event["type"],
                "message": event["message"]
            }

            row.update(event["data"])

            rows.append(row)

        return pd.DataFrame(rows)

    def save_csv(self, filename):

        df = self.to_dataframe()

        df.to_csv(filename, index=False)

    def clear(self):

        self.events.clear()