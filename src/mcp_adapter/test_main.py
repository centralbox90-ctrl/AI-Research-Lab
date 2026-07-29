from pathlib import Path

import pytest

import src.mcp_adapter.__main__ as mcp_main
from src.storage import (
    RESEARCH_CYCLE_DATABASE_PATH,
)


class StubMcpServer:
    def __init__(self) -> None:
        self.run_calls = 0

    def run(self) -> None:
        self.run_calls += 1


def configure_stub_server(
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[
    StubMcpServer,
    list[Path],
]:
    server = StubMcpServer()
    database_paths: list[Path] = []

    def build_server(
        db_path: str | Path,
    ) -> StubMcpServer:
        database_paths.append(
            Path(db_path)
        )

        return server

    monkeypatch.setattr(
        mcp_main,
        "build_research_mcp_server",
        build_server,
    )

    return server, database_paths


def test_runs_stdio_server_with_default_database(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    (
        server,
        database_paths,
    ) = configure_stub_server(
        monkeypatch
    )

    exit_code = mcp_main.main([])

    assert exit_code == 0
    assert database_paths == [
        Path(RESEARCH_CYCLE_DATABASE_PATH),
    ]
    assert server.run_calls == 1


def test_runs_stdio_server_with_explicit_database(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    (
        server,
        database_paths,
    ) = configure_stub_server(
        monkeypatch
    )
    database_path = (
        tmp_path / "research-cycles.db"
    )

    exit_code = mcp_main.main(
        [
            "--database",
            str(database_path),
        ]
    )

    assert exit_code == 0
    assert database_paths == [
        database_path,
    ]
    assert server.run_calls == 1
