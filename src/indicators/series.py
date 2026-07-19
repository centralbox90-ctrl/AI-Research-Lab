from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime
from types import MappingProxyType
from typing import Any

from src.indicators.specification import IndicatorSpecification


@dataclass(frozen=True, slots=True)
class IndicatorSeries:
    """
    Результат воспроизводимого расчёта индикатора.

    Каждое значение должно соответствовать timestamp
    с тем же индексом.
    """

    specification: IndicatorSpecification
    timestamps: tuple[datetime, ...]
    values: tuple[float | None, ...]
    warmup_bars: int
    source_data_ref: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        timestamps = tuple(self.timestamps)
        values = tuple(self.values)

        if len(timestamps) != len(values):
            raise ValueError(
                "timestamps and values must have equal length"
            )

        if self.warmup_bars < 0:
            raise ValueError(
                "warmup_bars must be greater than or equal to zero"
            )

        if self.warmup_bars > len(values):
            raise ValueError(
                "warmup_bars must not exceed series length"
            )

        if self.source_data_ref is not None:
            source_data_ref = self.source_data_ref.strip()

            if not source_data_ref:
                raise ValueError(
                    "source_data_ref must not be empty when provided"
                )

            object.__setattr__(
                self,
                "source_data_ref",
                source_data_ref,
            )

        object.__setattr__(
            self,
            "timestamps",
            timestamps,
        )
        object.__setattr__(
            self,
            "values",
            values,
        )
        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(dict(self.metadata)),
        )

    @property
    def valid_from(self) -> int | None:
        """
        Индекс первого валидного значения.

        Возвращает None, если валидных значений нет.
        """
        for index, value in enumerate(self.values):
            if value is not None:
                return index

        return None

    def __len__(self) -> int:
        return len(self.values)

    def value_at(self, index: int) -> float | None:
        return self.values[index]

    def timestamp_at(self, index: int) -> datetime:
        return self.timestamps[index]

    @classmethod
    def create(
        cls,
        *,
        specification: IndicatorSpecification,
        timestamps: Sequence[datetime],
        values: Sequence[float | None],
        warmup_bars: int,
        source_data_ref: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> "IndicatorSeries":
        return cls(
            specification=specification,
            timestamps=tuple(timestamps),
            values=tuple(values),
            warmup_bars=warmup_bars,
            source_data_ref=source_data_ref,
            metadata={} if metadata is None else metadata,
        )