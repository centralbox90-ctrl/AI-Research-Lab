from __future__ import annotations

from pathlib import Path

from flask import Flask

from src.api.research_api import (
    create_research_api,
)
from src.application.public_api import (
    ListStoredResearchCycles,
)
from src.storage import (
    RESEARCH_CYCLE_DATABASE_PATH,
    SqliteResearchCycleStore,
)


def build_research_api(
    db_path: str | Path = (
        RESEARCH_CYCLE_DATABASE_PATH
    ),
) -> Flask:
    """
    Build the production HTTP dependency graph.

    Infrastructure is selected only in this composition root.
    """

    store = SqliteResearchCycleStore(
        db_path=db_path,
    )
    list_stored_research_cycles = (
        ListStoredResearchCycles(
            store=store,
        )
    )

    return create_research_api(
        list_stored_research_cycles=(
            list_stored_research_cycles
        ),
    )