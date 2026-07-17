from __future__ import annotations

import subprocess
from pathlib import Path


class GitCommandRunner:
    def read_head_commit(
        self,
        repository_path: Path,
    ) -> str:
        completed = subprocess.run(
            [
                "git",
                "rev-parse",
                "HEAD",
            ],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )

        return completed.stdout.strip()
