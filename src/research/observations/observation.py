from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class Observation:
    """
    Конкретный зафиксированный случай наблюдаемого события.
    """

    id: str
    definition_id: str
    symbol: str
    timeframe: str
    timestamp: datetime
    bar_index: int
    price: float
    context: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("id must not be empty")

        if not self.definition_id.strip():
            raise ValueError("definition_id must not be empty")

        if not self.symbol.strip():
            raise ValueError("symbol must not be empty")

        if not self.timeframe.strip():
            raise ValueError("timeframe must not be empty")

        if self.bar_index < 0:
            raise ValueError(
                "bar_index must be greater than or equal to zero"
            )