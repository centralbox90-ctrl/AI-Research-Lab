from __future__ import annotations

import importlib
import pkgutil
from collections.abc import Iterable
from types import ModuleType

from src.indicators.descriptor import IndicatorDescriptor


DEFAULT_IMPLEMENTATIONS_PACKAGE = "src.indicators.implementations"


class IndicatorDiscoveryError(RuntimeError):
    """Ошибка при обнаружении indicator plugin."""


def discover_indicators(
    package_name: str = DEFAULT_IMPLEMENTATIONS_PACKAGE,
) -> tuple[IndicatorDescriptor, ...]:
    """
    Находит indicator plugins внутри указанного пакета.

    Каждый plugin должен экспортировать переменную INDICATOR.
    Discovery ничего не регистрирует и не создаёт глобальный catalog.
    """
    package = _import_package(package_name)
    indicators: list[IndicatorDescriptor] = []
    indicator_modules: dict[str, str] = {}

    for module_name in sorted(_iter_module_names(package)):
        module = importlib.import_module(module_name)

        if not hasattr(module, "INDICATOR"):
            continue

        indicator = getattr(module, "INDICATOR")

        if indicator is None:
            raise IndicatorDiscoveryError(
                f"Module '{module_name}' exports INDICATOR=None."
            )

        if not isinstance(indicator, IndicatorDescriptor):
            raise IndicatorDiscoveryError(
                f"Module '{module_name}' exports an invalid "
                "INDICATOR value. Expected IndicatorDescriptor, "
                f"got {type(indicator).__name__}."
            )

        existing_module = indicator_modules.get(indicator.id)

        if existing_module is not None:
            raise IndicatorDiscoveryError(
                f"Duplicate indicator id '{indicator.id}' exported by "
                f"modules '{existing_module}' and '{module_name}'."
            )

        indicator_modules[indicator.id] = module_name
        indicators.append(indicator)

    return tuple(indicators)


def _import_package(package_name: str) -> ModuleType:
    try:
        package = importlib.import_module(package_name)
    except ModuleNotFoundError as error:
        raise IndicatorDiscoveryError(
            f"Indicator implementations package "
            f"'{package_name}' was not found."
        ) from error

    if not hasattr(package, "__path__"):
        raise IndicatorDiscoveryError(
            f"'{package_name}' is not a package."
        )

    return package


def _iter_module_names(package: ModuleType) -> Iterable[str]:
    prefix = f"{package.__name__}."

    for module_info in pkgutil.iter_modules(
        package.__path__,
        prefix,
    ):
        if module_info.ispkg:
            continue

        yield module_info.name
