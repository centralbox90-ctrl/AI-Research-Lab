from __future__ import annotations

from pathlib import Path

from flask import Flask

from src.api.research_api import (
    create_research_api,
)
from src.application.artifact_comparison_input_extractor import (
    ArtifactComparisonInputExtractor,
)
from src.application.public_api import (
    CompareStoredResearchArtifacts,
    GetStoredResearchArtifact,
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
    *,
    api_token: str | None = None,
) -> Flask:
    """
    Build the production HTTP dependency graph.

    Infrastructure is selected only in this composition root.
    """

    store = SqliteResearchCycleStore(
        db_path=db_path,
    )
    get_stored_research_artifact = (
        GetStoredResearchArtifact(
            store=store,
        )
    )
    list_stored_research_cycles = (
        ListStoredResearchCycles(
            store=store,
        )
    )
    compare_stored_research_artifacts = (
        CompareStoredResearchArtifacts(
            artifact_getter=(
                get_stored_research_artifact
            ),
            input_extractor=(
                ArtifactComparisonInputExtractor()
            ),
        )
    )

    return create_research_api(
        compare_stored_research_artifacts=(
            compare_stored_research_artifacts
        ),
        get_stored_research_artifact=(
            get_stored_research_artifact
        ),
        list_stored_research_cycles=(
            list_stored_research_cycles
        ),
        api_token=api_token,
        readiness_check=store.is_ready,
    )