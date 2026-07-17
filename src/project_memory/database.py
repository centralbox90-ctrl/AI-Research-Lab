import sqlite3
from pathlib import Path

from .config import DATABASE_PATH
from .event import ProjectEvent


class ProjectDatabase:

    def __init__(
        self,
        db_path: str | Path = DATABASE_PATH,
    ):

        self.db_path = Path(db_path)

        self.db_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.create_tables()

    def get_connection(self):

        return sqlite3.connect(self.db_path)

    def create_tables(self):

        connection = self.get_connection()

        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS events(

                id TEXT PRIMARY KEY,

                timestamp TEXT,

                event_type TEXT,

                file_path TEXT,

                is_directory INTEGER

            )
            """
        )

        connection.commit()

        connection.close()

    def save_event(
        self,
        event: ProjectEvent,
    ):

        connection = self.get_connection()

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO events
            VALUES(?,?,?,?,?)
            """,
            (
                event.id,
                event.timestamp.isoformat(),
                event.event_type.value,
                event.file_path,
                int(event.is_directory),
            ),
        )

        connection.commit()

        connection.close()