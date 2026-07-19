from abc import ABC, abstractmethod

from src.research.observations.definition import (
    ObservationDefinition,
)
from src.research.observations.observation import Observation


class ObservationProvider(ABC):
    """
    Контракт источника наблюдений.
    """

    @abstractmethod
    def find(
        self,
        definition: ObservationDefinition,
    ) -> list[Observation]:
        ...