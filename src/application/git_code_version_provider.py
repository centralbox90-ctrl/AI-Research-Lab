from __future__ import annotations

import subprocess
from pathlib import Path

from .ports.git_commit_reader import GitCommitReader


class GitCodeVersionProvider:
    """
    Returns the current Git commit as a code version identifier.

    If Git metadata is unavailable, returns the configured fallback.
    """

    def __init__(
        self,
        *,
        git_commit_reader: GitCommitReader,
        repository_path: Path | None = None,
        fallback: str = "unknown",
    ) -> None:
        if (
            not isinstance(fallback, str)
            or not fallback.strip()
        ):
            raise ValueError(
                "fallback must be a non-empty string"
            )

        self._repository_path = (
            repository_path or Path.cwd()
        )
        self._fallback = fallback.strip()
        self._git_commit_reader = git_commit_reader

    def get_code_version(self) -> str:
        try:
            commit = self._git_commit_reader.read_head_commit(
                self._repository_path,
            )
        except (
            OSError,
            subprocess.CalledProcessError,
        ):
            commit = ""

        if not commit:
            return self._fallback

        return f"git:{commit}"
