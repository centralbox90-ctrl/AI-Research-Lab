from __future__ import annotations

import subprocess
from pathlib import Path


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

    def get_code_version(self) -> str:
        try:
            commit = self._read_git_commit()
        except (
            OSError,
            subprocess.CalledProcessError,
        ):
            return self._fallback

        if not commit:
            return self._fallback

        return f"git:{commit}"

    def _read_git_commit(self) -> str:
        completed = subprocess.run(
            [
                "git",
                "rev-parse",
                "HEAD",
            ],
            cwd=self._repository_path,
            capture_output=True,
            text=True,
            check=True,
        )

        return completed.stdout.strip()
