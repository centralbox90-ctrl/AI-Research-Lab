from pathlib import Path


PROJECT_ROOT = Path(".").resolve()

RESEARCH_STORAGE_DIR = PROJECT_ROOT / ".research_lab"

RESEARCH_CYCLE_DATABASE_PATH = (
    RESEARCH_STORAGE_DIR / "research_cycles.db"
)