from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from typing import Any
from uuid import UUID

import numpy as np

from src.research import NextExperimentResearchCycleResult


class ResearchCycleSerializer:
    """
    Serializes a completed research cycle into application-safe data.

    The serializer does not change the research domain models and does
    not depend on a specific CLI, HTTP framework, or database.
    """

    def serialize(
        self,
        cycle: NextExperimentResearchCycleResult,
    ) -> dict[str, Any]:
        serialized = self._serialize_value(cycle)

        if not isinstance(serialized, dict):
            raise TypeError(
                "Serialized research cycle must be a dictionary."
            )

        return serialized

    def _serialize_value(self, value: Any) -> Any:
        if is_dataclass(value) and not isinstance(value, type):
            return {
                key: self._serialize_value(item)
                for key, item in asdict(value).items()
            }

        if isinstance(value, dict):
            return {
                str(key): self._serialize_value(item)
                for key, item in value.items()
            }

        if isinstance(value, (list, tuple, set)):
            return [
                self._serialize_value(item)
                for item in value
            ]

        if isinstance(value, np.ndarray):
            return [
                self._serialize_value(item)
                for item in value.tolist()
            ]

        if isinstance(value, np.generic):
            return self._serialize_value(
                value.item()
            )

        if isinstance(value, (datetime, date)):
            return value.isoformat()

        if isinstance(value, UUID):
            return str(value)

        return value