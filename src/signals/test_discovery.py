from __future__ import annotations

import sys
from pathlib import Path

import pytest

from src.signals.discovery import (
    SignalRuleDiscoveryError,
    discover_signal_rules,
)


def create_package(
    root: Path,
    package_name: str,
) -> Path:
    package_path = root.joinpath(
        *package_name.split(".")
    )
    package_path.mkdir(parents=True)

    package_path.joinpath("__init__.py").write_text(
        "",
        encoding="utf-8",
    )

    return package_path


def clear_modules(package_name: str) -> None:
    module_names = [
        module_name
        for module_name in sys.modules
        if (
            module_name == package_name
            or module_name.startswith(
                f"{package_name}."
            )
        )
    ]

    for module_name in module_names:
        sys.modules.pop(module_name, None)


def test_rejects_duplicate_signal_rule_ids(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    package_name = (
        "temporary_signal_rules_with_duplicate_ids"
    )
    package_path = create_package(
        tmp_path,
        package_name,
    )

    plugin_code = """
from src.signals.descriptor import SignalRuleDescriptor


class StubSignalRule:
    def generate(self, series, observations):
        return ()


SIGNAL_RULE = SignalRuleDescriptor(
    rule_id="duplicate",
    version=1,
    rule=StubSignalRule(),
)
"""

    package_path.joinpath("first.py").write_text(
        plugin_code,
        encoding="utf-8",
    )
    package_path.joinpath("second.py").write_text(
        plugin_code,
        encoding="utf-8",
    )

    monkeypatch.syspath_prepend(str(tmp_path))
    clear_modules(package_name)

    with pytest.raises(
        SignalRuleDiscoveryError,
        match="Duplicate signal rule id 'duplicate'",
    ):
        discover_signal_rules(package_name)