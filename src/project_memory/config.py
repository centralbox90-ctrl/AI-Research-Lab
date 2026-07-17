from pathlib import Path


PROJECT_ROOT = Path(".").resolve()

DATABASE_DIR = PROJECT_ROOT / ".project_memory"

DATABASE_PATH = DATABASE_DIR / "events.db"

SNAPSHOT_DIR = DATABASE_DIR / "snapshots"


IGNORED_DIRECTORIES = {

    ".git",

    ".project_memory",

    ".venv",

    "__pycache__",

    ".pytest_cache",

    ".mypy_cache",

    ".idea",

    ".vscode",

}


IGNORED_EXTENSIONS = {

    ".pyc",

    ".log",

}