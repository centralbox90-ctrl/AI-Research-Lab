from __future__ import annotations

import importlib
import pkgutil
from collections.abc import Iterable
from types import ModuleType

from src.application.observation_calculation_service import (
    ObservationDescriptor,
)


DEFAULT_IMPLEMENTATIONS_PACKAGE = (
    "src.application.observations.implementations"
)


class ObservationDiscoveryError(RuntimeError):
    """Ошибка обнаружения observation plugin."""


def discover_observations(
    package_name: str = DEFAULT_IMPLEMENTATIONS_PACKAGE,
) -> tuple[ObservationDescriptor, ...]:
    """
    Finds registered observation plugins.

    Each plugin must export OBSERVATION.
    """

    package = _import_package(package_name)

    descriptors: list[ObservationDescriptor] = []

    for module_name in _iter_module_names(package):
        module = importlib.import_module(module_name)

        if not hasattr(module, "OBSERVATION"):
            continue

        observation = getattr(
            module,
            "OBSERVATION",
        )

        if not isinstance(
            observation,
            ObservationDescriptor,
        ):
            raise ObservationDiscoveryError(
                f"Module '{module_name}' exports invalid "
                "OBSERVATION."
            )

        descriptors.append(observation)

    return tuple(descriptors)


def _import_package(
    package_name: str,
) -> ModuleType:

    try:
        package = importlib.import_module(
            package_name,
        )
    except ModuleNotFoundError as error:
        raise ObservationDiscoveryError(
            f"Package '{package_name}' not found."
        ) from error

    if not hasattr(package, "__path__"):
        raise ObservationDiscoveryError(
            f"'{package_name}' is not a package."
        )

    return package


def _iter_module_names(
    package: ModuleType,
) -> Iterable[str]:

    prefix = f"{package.__name__}."

    for module_info in pkgutil.iter_modules(
        package.__path__,
        prefix,
    ):
        if module_info.ispkg:
            continue

        yield module_info.name