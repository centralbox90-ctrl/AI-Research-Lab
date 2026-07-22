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

def test_each_production_module_is_one_discoverable_indicator() -> None:
    implementations_path = Path(
        "src/indicators/implementations"
    )

    module_names = {
        path.stem
        for path in implementations_path.glob("*.py")
        if path.name != "__init__.py"
    }

    discovered_indicator_ids = {
        indicator.id
        for indicator in discover_indicators()
    }

    assert discovered_indicator_ids == module_names

def test_rejects_duplicate_indicator_ids(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    package_name = "temporary_indicators_with_duplicate_ids"
    package_path = create_package(
        tmp_path,
        package_name,
    )

    plugin_code = """
from src.indicators.descriptor import IndicatorDescriptor


def calculator(data, specification):
    raise NotImplementedError


INDICATOR = IndicatorDescriptor(
    id="duplicate",
    symbol="{symbol}",
    name="{name}",
    version=1,
    calculator=calculator,
)
"""

    package_path.joinpath("first.py").write_text(
        plugin_code.format(
            symbol="FIRST",
            name="First",
        ),
        encoding="utf-8",
    )

    package_path.joinpath("second.py").write_text(
        plugin_code.format(
            symbol="SECOND",
            name="Second",
        ),
        encoding="utf-8",
    )

    monkeypatch.syspath_prepend(str(tmp_path))
    clear_modules(package_name)

    with pytest.raises(
        IndicatorDiscoveryError,
        match="Duplicate indicator id 'duplicate'",
    ):
        discover_indicators(package_name)

def test_discovers_indicators_in_module_name_order(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    package_name = "temporary_indicators_with_order"
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
)
"""

    package_path.joinpath("zeta.py").write_text(
        plugin_code.format(
            indicator_id="zeta",
            symbol="ZETA",
            name="Zeta",
        ),
        encoding="utf-8",
    )

    package_path.joinpath("alpha.py").write_text(
        plugin_code.format(
            indicator_id="alpha",
            symbol="ALPHA",
            name="Alpha",
        ),
        encoding="utf-8",
    )

    monkeypatch.syspath_prepend(str(tmp_path))
    clear_modules(package_name)

    indicators = discover_indicators(package_name)

    assert tuple(
        indicator.id
        for indicator in indicators
    ) == (
        "alpha",
        "zeta",
    )


def test_discovers_indicator_plugin() -> None:
    indicators = discover_indicators()

    assert indicators
    assert all(indicator.id for indicator in indicators)
    assert all(indicator.symbol for indicator in indicators)
    assert all(indicator.name for indicator in indicators)
