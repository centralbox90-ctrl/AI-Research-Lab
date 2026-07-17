from __future__ import annotations

from pathlib import Path
from typing import Protocol


class GitCommitReader(Protocol):
    def read_head_commit(
        self,
        repository_path: Path,
    ) -> str:
        ...
