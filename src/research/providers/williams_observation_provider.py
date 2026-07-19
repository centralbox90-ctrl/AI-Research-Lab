from src.research.observation import Observation
from src.research.observation_definition import ObservationDefinition
from src.research.observation_provider import ObservationProvider


class WilliamsObservationProvider(ObservationProvider):
    """
    Ищет наблюдения Williams %R.

    Пока является каркасом.
    Логика поиска будет перенесена из существующего ResearchEngine
    на следующем этапе.
    """

    def find(
        self,
        definition: ObservationDefinition,
    ) -> list[Observation]:
        return []