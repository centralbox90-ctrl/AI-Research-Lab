from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from uuid import uuid4


class EventType(Enum):

    CREATED = "CREATED"

    MODIFIED = "MODIFIED"

    DELETED = "DELETED"

    MOVED = "MOVED"


@dataclass(slots=True)
class ProjectEvent:

    id: str

    event_type: EventType

    file_path: str

    timestamp: datetime

    is_directory: bool = False


    @staticmethod
    def create(
        event_type: EventType,
        path: str,
        is_directory: bool = False
    ) -> "ProjectEvent":

        return ProjectEvent(
            id=str(uuid4()),
            event_type=event_type,
            file_path=str(Path(path)),
            timestamp=datetime.now(),
            is_directory=is_directory,
        )