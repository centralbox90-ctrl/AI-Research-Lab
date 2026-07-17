from __future__ import annotations

from typing import Protocol


class CodeVersionProvider(Protocol):
    """
    Supplies the version identifier of the code used by a research run.
    """

    def get_code_version(self) -> str:
        """
        Return a non-empty reproducible code version identifier.
        """
        ...


class StaticCodeVersionProvider:
    """
    Returns a code version supplied by the composition root.

    Useful for tests and environments where Git metadata is unavailable.
    """

    def __init__(
        self,
        code_version: str,
    ) -> None:
        if (
            not isinstance(code_version, str)
            or not code_version.strip()
        ):
            raise ValueError(
                "code_version must be a non-empty string"
            )

        self._code_version = code_version.strip()

    def get_code_version(self) -> str:
        return self._code_version