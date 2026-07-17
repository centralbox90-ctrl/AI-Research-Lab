from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from .git_code_version_provider import GitCodeVersionProvider


class StubGitCommitReader:
    def __init__(
        self,
        *,
        commit: str = "",
        error: Exception | None = None,
    ) -> None:
        self._commit = commit
        self._error = error

    def read_head_commit(
        self,
        repository_path: Path,
    ) -> str:
        if self._error is not None:
            raise self._error

        return self._commit


def test_provider_returns_git_commit() -> None:
    git_commit_reader = StubGitCommitReader(
        commit="abc123",
    )

    provider = GitCodeVersionProvider(
        git_commit_reader=git_commit_reader,
        repository_path=Path("."),
    )

    assert provider.get_code_version() == "git:abc123"


def test_provider_returns_fallback_when_git_fails() -> None:
    git_commit_reader = StubGitCommitReader(
        error=subprocess.CalledProcessError(
            1,
            "git",
        ),
    )

    provider = GitCodeVersionProvider(
        git_commit_reader=git_commit_reader,
        fallback="unknown",
    )

    assert provider.get_code_version() == "unknown"


@pytest.mark.parametrize(
    "value",
    [
        "",
        "   ",
    ],
)
def test_provider_rejects_empty_fallback(
    value: str,
) -> None:
    git_commit_reader = StubGitCommitReader()

    with pytest.raises(
        ValueError,
        match="fallback must be a non-empty string",
    ):
        GitCodeVersionProvider(
            git_commit_reader=git_commit_reader,
            fallback=value,
        )
