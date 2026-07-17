import importlib
import runpy

import pytest


def test_cli_package_entry_point_delegates_to_main(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    received = {
        "called": False,
    }

    def fake_main() -> int:
        received["called"] = True
        return 7

    main_module = importlib.import_module("src.cli.main")

    monkeypatch.setattr(
        main_module,
        "main",
        fake_main,
    )

    with pytest.raises(SystemExit) as error:
        runpy.run_module(
            "src.cli.__main__",
            run_name="__main__",
        )

    assert received["called"] is True
    assert error.value.code == 7