from __future__ import annotations

import importlib
import pkgutil
from collections.abc import Iterable
from types import ModuleType

from src.signals.descriptor import (
    SignalRuleDescriptor,
)


DEFAULT_SIGNAL_RULES_PACKAGE = (
    "src.signals.implementations"
)


class SignalRuleDiscoveryError(RuntimeError):
    """
    Ошибка обнаружения signal rule plugin.
    """


def discover_signal_rules(
    package_name: str = DEFAULT_SIGNAL_RULES_PACKAGE,
) -> tuple[SignalRuleDescriptor, ...]:
    """
    Finds signal rule plugins.

    Each plugin must export:

        SIGNAL_RULE

    Discovery does not register rules globally.
    """

    package = _import_package(
        package_name
    )

    rules: list[SignalRuleDescriptor] = []
    discovered_rule_ids: set[str] = set()

    for module_name in _iter_module_names(
        package
    ):
        module = importlib.import_module(
            module_name
        )

        if not hasattr(
            module,
            "SIGNAL_RULE",
        ):
            continue

        signal_rule = getattr(
            module,
            "SIGNAL_RULE",
        )

        if signal_rule is None:
            raise SignalRuleDiscoveryError(
                f"Module '{module_name}' "
                "exports SIGNAL_RULE=None."
            )

        if not isinstance(
            signal_rule,
            SignalRuleDescriptor,
        ):
            raise SignalRuleDiscoveryError(
                f"Module '{module_name}' "
                "exports invalid SIGNAL_RULE. "
                "Expected SignalRuleDescriptor."
            )

        rules.append(
            signal_rule
        )

    return tuple(rules)


def _import_package(
    package_name: str,
) -> ModuleType:
    try:
        package = importlib.import_module(
            package_name
        )

    except ModuleNotFoundError as error:
        raise SignalRuleDiscoveryError(
            f"Signal rule package "
            f"'{package_name}' was not found."
        ) from error

    if not hasattr(
        package,
        "__path__",
    ):
        raise SignalRuleDiscoveryError(
            f"'{package_name}' is not a package."
        )

    return package


def _iter_module_names(
    package: ModuleType,
) -> Iterable[str]:

    prefix = (
        f"{package.__name__}."
    )

    for module_info in pkgutil.iter_modules(
        package.__path__,
        prefix,
    ):
        if module_info.ispkg:
            continue

        yield module_info.name