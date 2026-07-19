from __future__ import annotations

import sys
from pathlib import Path

import pytest

from src.indicators.discovery import (
    IndicatorDiscoveryError,
    discover_indicators,
)


def create_package(
    root: Path,
    package_name: str,
) -> Path:
    package_path = root.joinpath(*package_name.split("."))
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
            or module_name.startswith(f"{package_name}.")
        )
    ]

    for module_name in module_names:
        sys.modules.pop(module_name, None)


def test_discovers_exported_indicators(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    package_name = "temporary_indicators"
    package_path = create_package(
        tmp_path,
        package_name,
    )

    plugin_code = """
from src.indicators.descriptor import IndicatorDescriptor


def calculator(data, specification):
    raise NotImplementedError


INDICATOR = IndicatorDescriptor(
    id="{indicator_id}",
    symbol="{symbol}",
    name="{name}",
    version=1,
    calculator=calculator,
    default_parameters={{}},
)
"""

    package_path.joinpath("first.py").write_text(
        plugin_code.format(
            indicator_id="first",
            symbol="FIRST",
            name="First",
        ),
        encoding="utf-8",
    )

    package_path.joinpath("second.py").write_text(
        plugin_code.format(
            indicator_id="second",
            symbol="SECOND",
            name="Second",
        ),
        encoding="utf-8",
    )

    monkeypatch.syspath_prepend(str(tmp_path))
    clear_modules(package_name)

    indicators = discover_indicators(package_name)

    assert {
        indicator.id
        for indicator in indicators
    } == {
        "first",
        "second",
    }


def test_ignores_modules_without_indicator_export(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    package_name = "temporary_indicators_without_export"
    package_path = create_package(
        tmp_path,
        package_name,
    )

    package_path.joinpath("helper.py").write_text(
        "VALUE = 1\n",
        encoding="utf-8",
    )

    monkeypatch.syspath_prepend(str(tmp_path))
    clear_modules(package_name)

    assert discover_indicators(package_name) == ()


def test_rejects_none_indicator_export(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    package_name = "temporary_indicators_with_none"
    package_path = create_package(
        tmp_path,
        package_name,
    )

    package_path.joinpath("broken.py").write_text(
        "INDICATOR = None\n",
        encoding="utf-8",
    )

    monkeypatch.syspath_prepend(str(tmp_path))
    clear_modules(package_name)

    with pytest.raises(
        IndicatorDiscoveryError,
        match="INDICATOR=None",
    ):
        discover_indicators(package_name)


def test_rejects_invalid_indicator_export(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    package_name = "temporary_indicators_with_invalid_export"
    package_path = create_package(
        tmp_path,
        package_name,
    )

    package_path.joinpath("broken.py").write_text(
        'INDICATOR = "not-a-descriptor"\n',
        encoding="utf-8",
    )

    monkeypatch.syspath_prepend(str(tmp_path))
    clear_modules(package_name)

    with pytest.raises(
        IndicatorDiscoveryError,
        match="Expected IndicatorDescriptor, got str",
    ):
        discover_indicators(package_name)


def test_rejects_missing_package() -> None:
    with pytest.raises(
        IndicatorDiscoveryError,
        match="was not found",
    ):
        discover_indicators(
            "package_that_does_not_exist",
        )
