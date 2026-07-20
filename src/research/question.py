from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

from src.research.research_types import ResearchStatus, ResearchType


@dataclass(frozen=True, slots=True)
class Question:
    """
    РСЃСЃР»РµРґРѕРІР°С‚РµР»СЊСЃРєРёР№ РІРѕРїСЂРѕСЃ.

    РћС‚РїСЂР°РІРЅР°СЏ С‚РѕС‡РєР° РёСЃСЃР»РµРґРѕРІР°РЅРёСЏ РІ AI Research Lab.
    """

    id: str = field(default_factory=lambda: str(uuid4()))

    title: str = ""

    description: str = ""

    research_type: ResearchType = ResearchType.HYPOTHESIS_TEST

    status: ResearchStatus = ResearchStatus.NEW

    created_at: datetime = field(default_factory=datetime.now)

    tags: list[str] = field(default_factory=list)

    notes: str = ""

    def summary(self) -> str:
        return (
            f"Question: {self.title}\n"
            f"ID: {self.id}\n"
            f"Type: {self.research_type}\n"
            f"Status: {self.status}\n"
            f"Tags: {', '.join(self.tags)}"
        )


@dataclass(frozen=True, slots=True)
class ResearchQuestion:
    """A market-behavior question to be investigated."""

    statement: str
    description: str = ""
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    status: ResearchStatus = ResearchStatus.NEW

    def __post_init__(self) -> None:
        if not isinstance(self.id, str):
            raise TypeError("id must be a string.")

        if not self.id.strip():
            raise ValueError("id must not be empty.")

        if not isinstance(self.statement, str):
            raise TypeError("statement must be a string.")

        if not self.statement.strip():
            raise ValueError("statement must not be empty.")

        if not isinstance(self.description, str):
            raise TypeError("description must be a string.")

        if not isinstance(self.created_at, datetime):
            raise TypeError("created_at must be a datetime.")

        if not isinstance(self.status, ResearchStatus):
            raise TypeError("status must be a ResearchStatus.")

    def to_dict(self) -> dict[str, str]:
        return {
            "id": self.id,
            "statement": self.statement,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "status": self.status.value,
        }
