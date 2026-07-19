from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class IndicatorSpecification:
    """
    Воспроизводимое описание конфигурации индикатора.

    Спецификация описывает алгоритм, его версию и параметры,
    но сама ничего не рассчитывает.
    """

    indicator_type: str
    version: int
    parameters: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        indicator_type = self.indicator_type.strip()

        if not indicator_type:
            raise ValueError("indicator_type must not be empty")

        if self.version < 1:
            raise ValueError("version must be greater than or equal to one")

        normalized_parameters = MappingProxyType(
            dict(self.parameters)
        )

        object.__setattr__(
            self,
            "indicator_type",
            indicator_type,
        )
        object.__setattr__(
            self,
            "parameters",
            normalized_parameters,
        )