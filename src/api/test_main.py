from pathlib import Path

import pytest

import src.api.__main__ as api_main
from src.storage import (
    RESEARCH_CYCLE_DATABASE_PATH,
)


class StubApplication:
    def __init__(self) -> None:
        self.run_calls: list[
            dict[str, object]
        ] = []

    def run(
        self,
        **options: object,
    ) -> None:
        self.run_calls.append(options)


def configure_stub_application(
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[
    StubApplication,
    list[Path],
]:
    application = StubApplication()
    database_paths: list[Path] = []

    def build_application(
        db_path: str | Path,
    ) -> StubApplication:
        database_paths.append(
            Path(db_path)
        )

        return application

    monkeypatch.setattr(
        api_main,
        "build_research_api",
        build_application,
    )

    return application, database_paths


def test_runs_local_api_with_safe_defaults(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    (
        application,
        database_paths,
    ) = configure_stub_application(
        monkeypatch
    )

    exit_code = api_main.main([])

    assert exit_code == 0
    assert database_paths == [
        Path(RESEARCH_CYCLE_DATABASE_PATH),
    ]
    assert application.run_calls == [
        {
            "host": "127.0.0.1",
            "port": 8000,
            "debug": False,
            "use_reloader": False,
        },
    ]


def test_runs_local_api_with_explicit_options(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    (
        application,
        database_paths,
    ) = configure_stub_application(
        monkeypatch
    )
    database_path = (
        tmp_path / "research-cycles.db"
    )

    exit_code = api_main.main(
        [
            "--database",
            str(database_path),
            "--host",
            "localhost",
            "--port",
            "8100",
        ]
    )

    assert exit_code == 0
    assert database_paths == [
        database_path,
    ]
    assert application.run_calls == [
        {
            "host": "localhost",
            "port": 8100,
            "debug": False,
            "use_reloader": False,
        },
    ]


@pytest.mark.parametrize(
    "value",
    [
        "0",
        "65536",
        "not-a-port",
    ],
)
def test_rejects_invalid_port(
    value: str,
) -> None:
    with pytest.raises(
        SystemExit,
    ) as error:
        api_main.main(
            [
                "--port",
                value,
            ]
        )

    assert error.value.code == 2


def test_rejects_empty_host() -> None:
    with pytest.raises(
        SystemExit,
    ) as error:
        api_main.main(
            [
                "--host",
                "   ",
            ]
        )

    assert error.value.code == 2