from __future__ import annotations

from collections.abc import Iterable

from src.indicators.descriptor import IndicatorDescriptor


class IndicatorCatalogError(RuntimeError):
    """Базовая ошибка каталога индикаторов."""


class DuplicateIndicatorError(IndicatorCatalogError):
    """Индикатор с таким id уже существует."""


class IndicatorNotFoundError(IndicatorCatalogError):
    """Индикатор не найден."""


class IndicatorCatalog:
    """Неизменяемый каталог indicator plugins."""

    def __init__(
        self,
        indicators: Iterable[IndicatorDescriptor],
    ) -> None:
        self._indicators: dict[str, IndicatorDescriptor] = {}

        for indicator in indicators:
            if indicator.id in self._indicators:
                raise DuplicateIndicatorError(
                    f"Duplicate indicator id '{indicator.id}'."
                )

            self._indicators[indicator.id] = indicator

    def get(
        self,
        indicator_id: str,
    ) -> IndicatorDescriptor:
        try:
            return self._indicators[indicator_id]
        except KeyError as error:
            raise IndicatorNotFoundError(
                f"Unknown indicator '{indicator_id}'."
            ) from error

    def contains(
        self,
        indicator_id: str,
    ) -> bool:
        return indicator_id in self._indicators

    @property
    def ids(self) -> tuple[str, ...]:
        return tuple(self._indicators)

    def __len__(self) -> int:
        return len(self._indicators)

    def __iter__(self):
        return iter(self._indicators.values())