from pathlib import Path

import pytest

import src.api.production_server as production_server
from src.storage import (
    RESEARCH_CYCLE_DATABASE_PATH,
)


VALID_API_TOKEN = (
    "test-private-api-token-0123456789abcdef"
)


class StubApplication:
    pass


class RecordingServe:
    def __init__(self) -> None:
        self.calls: list[
            tuple[
                object,
                dict[str, object],
            ]
        ] = []

    def __call__(
        self,
        application: object,
        **options: object,
    ) -> None:
        self.calls.append(
            (
                application,
                options,
            )
        )


def configure_production_server(
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[
    StubApplication,
    RecordingServe,
    list[Path],
]:
    monkeypatch.setenv(
        production_server.API_TOKEN_ENVIRONMENT_VARIABLE,
        VALID_API_TOKEN,
    )
    application = StubApplication()
    recording_serve = RecordingServe()
    database_paths: list[Path] = []

    def build_application(
        db_path: str | Path,
        *,
        api_token: str | None = None,
    ) -> StubApplication:
        assert api_token == VALID_API_TOKEN

        database_paths.append(
            Path(db_path)
        )

        return application

    monkeypatch.setattr(
        production_server,
        "build_research_api",
        build_application,
    )
    monkeypatch.setattr(
        production_server,
        "serve",
        recording_serve,
    )

    return (
        application,
        recording_serve,
        database_paths,
    )


def test_runs_waitress_with_safe_defaults(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    (
        application,
        recording_serve,
        database_paths,
    ) = configure_production_server(
        monkeypatch
    )

    exit_code = production_server.main([])

    assert exit_code == 0
    assert database_paths == [
        Path(RESEARCH_CYCLE_DATABASE_PATH),
    ]
    assert recording_serve.calls == [
        (
            application,
            {
                "host": "127.0.0.1",
                "port": 8080,
                "threads": 4,
            },
        ),
    ]


def test_runs_waitress_with_explicit_options(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    (
        application,
        recording_serve,
        database_paths,
    ) = configure_production_server(
        monkeypatch
    )
    database_path = (
        tmp_path / "research-cycles.db"
    )

    exit_code = production_server.main(
        [
            "--database",
            str(database_path),
            "--host",
            "localhost",
            "--port",
            "8100",
            "--threads",
            "8",
        ]
    )

    assert exit_code == 0
    assert database_paths == [
        database_path,
    ]
    assert recording_serve.calls == [
        (
            application,
            {
                "host": "localhost",
                "port": 8100,
                "threads": 8,
            },
        ),
    ]


def test_configures_production_logging(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configure_production_server(
        monkeypatch
    )
    configuration_calls: list[
        dict[str, object]
    ] = []

    def configure_logging(
        **options: object,
    ) -> None:
        configuration_calls.append(options)

    monkeypatch.setattr(
        production_server.logging,
        "basicConfig",
        configure_logging,
    )

    exit_code = production_server.main(
        [
            "--log-level",
            "WARNING",
        ]
    )

    assert exit_code == 0
    assert configuration_calls == [
        {
            "level": (
                production_server.logging.WARNING
            ),
            "format": production_server.LOG_FORMAT,
        },
    ]


def test_rejects_invalid_log_level(
) -> None:
    with pytest.raises(
        SystemExit,
    ) as error:
        production_server.main(
            [
                "--log-level",
                "VERBOSE",
            ]
        )

    assert error.value.code == 2


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
        production_server.main(
            [
                "--port",
                value,
            ]
        )

    assert error.value.code == 2


@pytest.mark.parametrize(
    "value",
    [
        "0",
        "-1",
        "not-a-number",
    ],
)
def test_rejects_invalid_thread_count(
    value: str,
) -> None:
    with pytest.raises(
        SystemExit,
    ) as error:
        production_server.main(
            [
                "--threads",
                value,
            ]
        )

    assert error.value.code == 2


def test_requires_production_api_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv(
        production_server.API_TOKEN_ENVIRONMENT_VARIABLE,
        raising=False,
    )

    with pytest.raises(
        SystemExit,
    ) as error:
        production_server.main([])

    assert error.value.code == 2


def test_rejects_invalid_production_api_tokens(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for value in (
        "",
        "short-token",
        f" {VALID_API_TOKEN}",
        "т" * 32,
    ):
        monkeypatch.setenv(
            production_server.API_TOKEN_ENVIRONMENT_VARIABLE,
            value,
        )

        with pytest.raises(
            SystemExit,
        ) as error:
            production_server.main([])

        assert error.value.code == 2


def test_accepts_loopback_hosts() -> None:
    assert production_server._parse_host(
        "localhost"
    ) == "localhost"
    assert production_server._parse_host(
        "127.0.0.2"
    ) == "127.0.0.2"
    assert production_server._parse_host(
        "::1"
    ) == "::1"


def test_rejects_non_loopback_hosts() -> None:
    for value in (
        "0.0.0.0",
        "::",
        "192.168.1.25",
        "research.example.com",
    ):
        with pytest.raises(
            SystemExit,
        ) as error:
            production_server.main(
                [
                    "--host",
                    value,
                ]
            )

        assert error.value.code == 2


def test_rejects_empty_host() -> None:
    with pytest.raises(
        SystemExit,
    ) as error:
        production_server.main(
            [
                "--host",
                "   ",
            ]
        )

    assert error.value.code == 2
