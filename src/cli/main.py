import argparse
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import TextIO

from src.application import (
    ExportStoredResearchArtifact,
    GetStoredResearchArtifact,
    GetStoredResearchCycle,
    ListStoredResearchCycles,
)
from src.application.artifact_comparison_input_extractor import (
    ArtifactComparisonInputExtractor,
)
from src.application.compare_stored_research_artifacts import (
    CompareStoredResearchArtifacts,
)
from src.application.generated_market_data_provider import (
    GeneratedMarketDataProvider,
)
from src.application.market_research_application import (
    build_market_research_application,
)
from src.application.simple_market_signal_provider import (
    SimpleMarketSignalProvider,
)
from src.cli.compare_research_artifacts_command import (
    CompareResearchArtifactsCommand,
)
from src.cli.export_research_artifact_command import (
    ExportResearchArtifactCommand,
)
from src.cli.get_stored_research_artifact_command import (
    GetStoredResearchArtifactCommand,
)
from src.cli.get_stored_research_cycle_command import (
    GetStoredResearchCycleCommand,
)
from src.cli.list_stored_research_cycles_command import (
    ListStoredResearchCyclesCommand,
)
from src.cli.research_cli import ResearchCli
from src.cli.run_market_research_command import (
    RunMarketResearchCommand,
)
from src.storage import (
    RESEARCH_CYCLE_DATABASE_PATH,
    SqliteResearchCycleStore,
)


def build_research_cli(
    db_path: str | Path = RESEARCH_CYCLE_DATABASE_PATH,
) -> ResearchCli:
    """
    Build the persistent AI Research Lab CLI dependency graph.

    All commands share one SQLite research-cycle store.
    """

    store = SqliteResearchCycleStore(
        db_path=db_path,
    )

    get_stored_cycle = GetStoredResearchCycle(
        store=store,
    )

    get_cycle_command = GetStoredResearchCycleCommand(
        get_stored_research_cycle=get_stored_cycle,
    )

    get_stored_artifact = GetStoredResearchArtifact(
        store=store,
    )

    get_artifact_command = (
        GetStoredResearchArtifactCommand(
            get_stored_research_artifact=get_stored_artifact,
        )
    )

    export_stored_artifact = ExportStoredResearchArtifact(
        get_stored_research_artifact=get_stored_artifact,
    )

    export_artifact_command = ExportResearchArtifactCommand(
        export_stored_research_artifact=(
            export_stored_artifact
        ),
    )

    compare_stored_artifacts = CompareStoredResearchArtifacts(
        artifact_getter=get_stored_artifact,
        input_extractor=ArtifactComparisonInputExtractor(),
    )

    compare_artifacts_command = CompareResearchArtifactsCommand(
        compare_stored_research_artifacts=(
            compare_stored_artifacts
        ),
    )

    list_stored_cycles = ListStoredResearchCycles(
        store=store,
    )

    list_command = ListStoredResearchCyclesCommand(
        list_stored_research_cycles=list_stored_cycles,
    )

    market_research_application = (
        build_market_research_application(
            data_provider=GeneratedMarketDataProvider(),
            signal_provider=SimpleMarketSignalProvider(),
            store=store,
        )
    )

    run_command = RunMarketResearchCommand(
        run_market_research=market_research_application,
    )

    return ResearchCli(
        get_research_cycle_command=get_cycle_command,
        get_research_artifact_command=get_artifact_command,
        export_research_artifact_command=(
            export_artifact_command
        ),
        compare_research_artifacts_command=(
            compare_artifacts_command
        ),
        list_research_cycles_command=list_command,
        run_research_command=run_command,
    )


def main(
    argv: Sequence[str] | None = None,
    *,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    """
    Run the AI Research Lab persistent CLI process.

    A custom database path may be supplied explicitly.
    """

    output_stream = stdout or sys.stdout
    error_stream = stderr or sys.stderr

    parser = argparse.ArgumentParser(
        prog="ai-research-lab",
        description=(
            "AI Research Lab persistent command-line interface."
        ),
        add_help=False,
    )

    parser.add_argument(
        "--database",
        default=str(RESEARCH_CYCLE_DATABASE_PATH),
        help=(
            "Path to the SQLite research-cycle database. "
            "Defaults to .research_lab/research_cycles.db."
        ),
    )

    try:
        arguments, remaining_arguments = parser.parse_known_args(
            argv,
        )
    except SystemExit as error:
        return int(error.code)

    cli = build_research_cli(
        db_path=arguments.database,
    )

    return cli.run(
        remaining_arguments,
        stdout=output_stream,
        stderr=error_stream,
    )


if __name__ == "__main__":
    raise SystemExit(main())