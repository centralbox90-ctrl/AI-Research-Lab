import argparse
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Protocol, TextIO


class ResearchCycleCommand(Protocol):
    """
    Command boundary for retrieving one research cycle.
    """

    def execute(
        self,
        result_id: str,
        *,
        indent: int | None = 2,
    ) -> str | None:
        """
        Return a research cycle as JSON or None when missing.
        """

class ResearchCampaignCommand(Protocol):
    """
    Command boundary for retrieving one research campaign.
    """

    def execute(
        self,
        campaign_id: str,
        *,
        indent: int | None = 2,
    ) -> str | None:
        """
        Return a research campaign as JSON or None when missing.
        """
class ResearchArtifactCommand(Protocol):
    """
    Command boundary for retrieving one research artifact.
    """

    def execute(
        self,
        result_id: str,
        *,
        indent: int | None = 2,
    ) -> str | None:
        """
        Return a research artifact as JSON or None when missing.
        """

class ExportResearchArtifactCommand(Protocol):
    """
    Command boundary for exporting one research artifact.
    """

    def execute(
        self,
        result_id: str,
        output_path: str | Path,
    ) -> str | None:
        """
        Export artifact and return output path.
        """


class CompareResearchArtifactsCommand(Protocol):
    """
    Command boundary for comparing two research artifacts.
    """

    def execute(
        self,
        artifact_a_result_id: str,
        artifact_b_result_id: str,
        *,
        indent: int | None = 2,
    ) -> str:
        """
        Compare two artifacts and return JSON.
        """


class ListResearchCyclesCommand(Protocol):
    """
    Command boundary for listing stored research-cycle IDs.
    """

    def execute(
        self,
        *,
        indent: int | None = 2,
    ) -> str:
        """
        Return stored research-cycle IDs as JSON.
        """

class ListResearchCampaignsCommand(Protocol):
    """
    Command boundary for listing stored research-campaign IDs.
    """

    def execute(
        self,
        *,
        indent: int | None = 2,
    ) -> str:
        """
        Return stored research-campaign IDs as JSON.
        """

class RunResearchCommand(Protocol):
    """
    Command boundary for running market research.
    """

    def execute(
        self,
        specification_path: str | Path,
        *,
        indent: int | None = 2,
    ) -> str:
        """
        Run research and return JSON.
        """


class ResearchCli:
    """
    Parses CLI arguments and delegates work to command handlers.
    """

    def __init__(
        self,
        get_research_cycle_command: ResearchCycleCommand,
        get_research_campaign_command: (
        ResearchCampaignCommand | None
        ) = None,
        list_research_cycles_command: (
            ListResearchCyclesCommand | None
        ) = None,
        run_research_command: RunResearchCommand | None = None,
        get_research_artifact_command: (
            ResearchArtifactCommand | None
        ) = None,
        export_research_artifact_command: (
            ExportResearchArtifactCommand | None
        ) = None,
        compare_research_artifacts_command: (
            CompareResearchArtifactsCommand | None
        ) = None,
        list_research_campaigns_command: (
            ListResearchCampaignsCommand | None
        ) = None,
    ) -> None:
        self.get_research_cycle_command = (
            get_research_cycle_command
        )
        self.get_research_campaign_command = (
            get_research_campaign_command
        )
        self.list_research_cycles_command = (
            list_research_cycles_command
        )
        self.list_research_campaigns_command = (
            list_research_campaigns_command
        )
        self.run_research_command = (
            run_research_command
        )

        self.get_research_artifact_command = (
            get_research_artifact_command
        )

        self.export_research_artifact_command = (
            export_research_artifact_command
        )

        self.compare_research_artifacts_command = (
            compare_research_artifacts_command
        )
        self.list_research_campaigns_command = (
             list_research_campaigns_command
        )

        self.parser = self._build_parser()

    def run(
        self,
        argv: Sequence[str] | None = None,
        *,
        stdout: TextIO | None = None,
        stderr: TextIO | None = None,
    ) -> int:
        output_stream = stdout or sys.stdout
        error_stream = stderr or sys.stderr

        try:
            arguments = self.parser.parse_args(argv)
        except SystemExit as error:
            return int(error.code)

        if arguments.command == "get-research-cycle":
            return self._run_get_research_cycle(
                arguments,
                output_stream,
                error_stream,
            )

        if arguments.command == "get-research-artifact":
            return self._run_get_research_artifact(
                arguments,
                output_stream,
                error_stream,
            )
        if arguments.command == "get-research-campaign":
            return self._run_get_research_campaign(
                arguments,
                output_stream,
                error_stream,
            )

        if arguments.command == "export-research-artifact":
            return self._run_export_research_artifact(
                arguments,
                output_stream,
                error_stream,
            )

        if arguments.command == "compare-research-artifacts":
            return self._run_compare_research_artifacts(
                arguments,
                output_stream,
                error_stream,
            )

        if arguments.command == "list-research-cycles":
            return self._run_list_research_cycles(
                arguments,
                output_stream,
                error_stream,
            )
        if arguments.command == "list-research-campaigns":
            return self._run_list_research_campaigns(
                arguments,
                output_stream,
                error_stream,
            )
        if arguments.command == "list-research-campaigns":
            return self._run_list_research_campaigns(
                arguments,
                output_stream,
                error_stream,
           )
        if arguments.command == "run-research":
            return self._run_market_research(
                arguments,
                output_stream,
                error_stream,
            )

        error_stream.write(
            "No CLI command was selected.\n"
        )

        return 2

    def _run_get_research_cycle(
        self,
        arguments: argparse.Namespace,
        stdout: TextIO,
        stderr: TextIO,
    ) -> int:
        indent = None if arguments.compact else 2

        rendered = self.get_research_cycle_command.execute(
            arguments.result_id,
            indent=indent,
        )

        if rendered is None:
            stderr.write(
                f"Research cycle not found: {arguments.result_id}\n"
            )
            return 1

        stdout.write(rendered)
        stdout.write("\n")

        return 0

    def _run_get_research_artifact(
        self,
        arguments: argparse.Namespace,
        stdout: TextIO,
        stderr: TextIO,
    ) -> int:
        if self.get_research_artifact_command is None:
            stderr.write(
                "Get research artifact command is not configured.\n"
            )
            return 2

        indent = None if arguments.compact else 2

        rendered = (
            self.get_research_artifact_command.execute(
                arguments.result_id,
                indent=indent,
            )
        )

        if rendered is None:
            stderr.write(
                f"Research artifact not found: {arguments.result_id}\n"
            )
            return 1

        stdout.write(rendered)
        stdout.write("\n")

        return 0

    def _run_export_research_artifact(
        self,
        arguments: argparse.Namespace,
        stdout: TextIO,
        stderr: TextIO,
    ) -> int:
        if self.export_research_artifact_command is None:
            stderr.write(
                "Export research artifact command is not configured.\n"
            )
            return 2

        exported_path = (
            self.export_research_artifact_command.execute(
                arguments.result_id,
                arguments.output_path,
            )
        )

        if exported_path is None:
            stderr.write(
                f"Research artifact not found: {arguments.result_id}\n"
            )
            return 1

        stdout.write(exported_path)
        stdout.write("\n")

        return 0

    def _run_compare_research_artifacts(
        self,
        arguments: argparse.Namespace,
        stdout: TextIO,
        stderr: TextIO,
    ) -> int:
        if self.compare_research_artifacts_command is None:
            stderr.write(
                "Compare research artifacts command is not configured.\n"
            )
            return 2

        indent = None if arguments.compact else 2

        try:
            rendered = (
                self.compare_research_artifacts_command.execute(
                    arguments.artifact_a_result_id,
                    arguments.artifact_b_result_id,
                    indent=indent,
                )
            )
        except ValueError as error:
            stderr.write(
                f"Unable to compare research artifacts: {error}\n"
            )
            return 1

        stdout.write(rendered)
        stdout.write("\n")

        return 0

    def _run_list_research_cycles(
        self,
        arguments: argparse.Namespace,
        stdout: TextIO,
        stderr: TextIO,
    ) -> int:
        if self.list_research_cycles_command is None:
            stderr.write(
                "List research cycles command is not configured.\n"
            )
            return 2

        indent = None if arguments.compact else 2

        rendered = self.list_research_cycles_command.execute(
            indent=indent,
        )

        stdout.write(rendered)
        stdout.write("\n")

        return 0

    def _run_list_research_campaigns(
        self,
        arguments: argparse.Namespace,
        stdout: TextIO,
        stderr: TextIO,
    ) -> int:
        if self.list_research_campaigns_command is None:
            stderr.write(
                "List research campaigns command is not configured.\n"
            )
            return 2

        indent = None if arguments.compact else 2

        rendered = self.list_research_campaigns_command.execute(
            indent=indent,
        )

        stdout.write(rendered)
        stdout.write("\n")

        return 0

    def _run_get_research_campaign(
        self,
        arguments: argparse.Namespace,
        stdout: TextIO,
        stderr: TextIO,
    ) -> int:
        if self.get_research_campaign_command is None:
            stderr.write(
                "Get research campaign command is not configured.\n"
            )
            return 2

        indent = None if arguments.compact else 2

        rendered = self.get_research_campaign_command.execute(
            arguments.campaign_id,
            indent=indent,
        )

        if rendered is None:
            stderr.write(
                f"Research campaign not found: {arguments.campaign_id}\n"
            )
            return 1

        stdout.write(rendered)
        stdout.write("\n")

        return 0

    def _run_market_research(
        self,
        arguments: argparse.Namespace,
        stdout: TextIO,
        stderr: TextIO,
    ) -> int:
        if self.run_research_command is None:
            stderr.write(
                "Run research command is not configured.\n"
            )
            return 2

        indent = None if arguments.compact else 2

        try:
            rendered = self.run_research_command.execute(
                arguments.specification_path,
                indent=indent,
            )
        except (ValueError, LookupError) as error:
            stderr.write(
                f"Unable to run research: {error}\n"
            )
            return 1

        stdout.write(rendered)
        stdout.write("\n")

        return 0
       
    def _build_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            prog="ai-research-lab",
            description="AI Research Lab command-line interface.",
        )

        subparsers = parser.add_subparsers(
            dest="command",
        )

        get_cycle_parser = subparsers.add_parser(
            "get-research-cycle",
        )

        get_cycle_parser.add_argument(
            "result_id",
        )

        get_cycle_parser.add_argument(
            "--compact",
            action="store_true",
        )
        get_campaign_parser = subparsers.add_parser(
           "get-research-campaign",
        )

        get_campaign_parser.add_argument(
            "campaign_id",
        )

        get_campaign_parser.add_argument(
            "--compact",
            action="store_true",
        )

        get_artifact_parser = subparsers.add_parser(
            "get-research-artifact",
            help="Return a saved research artifact as JSON.",
        )

        get_artifact_parser.add_argument(
            "result_id",
        )

        get_artifact_parser.add_argument(
            "--compact",
            action="store_true",
        )

        export_artifact_parser = subparsers.add_parser(
            "export-research-artifact",
            help="Export a saved research artifact to JSON file.",
        )

        export_artifact_parser.add_argument(
            "result_id",
        )

        export_artifact_parser.add_argument(
            "--output",
            dest="output_path",
            type=Path,
            required=True,
        )

        compare_artifacts_parser = subparsers.add_parser(
            "compare-research-artifacts",
            help="Compare two saved research artifacts.",
        )

        compare_artifacts_parser.add_argument(
            "artifact_a_result_id",
        )

        compare_artifacts_parser.add_argument(
            "artifact_b_result_id",
        )

        compare_artifacts_parser.add_argument(
            "--compact",
            action="store_true",
        )

        list_cycles_parser = subparsers.add_parser(
            "list-research-cycles",
        )
        list_campaigns_parser = subparsers.add_parser(
            "list-research-campaigns",
        )

        list_campaigns_parser.add_argument(
           "--compact",
           action="store_true",
        )

        list_cycles_parser.add_argument(
            "--compact",
            action="store_true",
        )

        run_research_parser = subparsers.add_parser(
            "run-research",
        )

        run_research_parser.add_argument(
            "--spec",
            dest="specification_path",
            type=Path,
            required=True,
        )

        run_research_parser.add_argument(
            "--compact",
            action="store_true",
        )

        return parser