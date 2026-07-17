from __future__ import annotations

import subprocess
from pathlib import Path

from .git_command_runner import GitCommandRunner


class GitCodeVersionProvider:
    """
    Returns the current Git commit as a code version identifier.

    If Git metadata is unavailable, returns the configured fallback.
    """

    def __init__(
        self,
        *,
        repository_path: Path | None = None,
        fallback: str = "unknown",
        git_command_runner: GitCommandRunner | None = None,
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
        self._git_command_runner = (
            git_command_runner
            or GitCommandRunner()
        )

    def get_code_version(self) -> str:
        try:
            commit = self._git_command_runner.read_head_commit(
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
