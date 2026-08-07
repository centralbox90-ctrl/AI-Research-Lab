import json
from io import StringIO

from src.cli.research_cli import ResearchCli


class StubGetCycleCommand:
    def execute(self, result_id, *, indent=2):
        return None


class StubParameterSearchCommand:
    def __init__(self) -> None:
        self.call = None

    def execute(self, **arguments):
        self.call = arguments
        return json.dumps(
            {
                "indicator_id": arguments["indicator_id"],
                "specification_count": 7688,
            },
            indent=arguments["indent"],
        )


def test_cli_runs_generic_indicator_parameter_search() -> None:
    command = StubParameterSearchCommand()
    cli = ResearchCli(
        StubGetCycleCommand(),
        run_indicator_parameter_search_command=command,
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = cli.run(
        [
            "run-indicator-parameter-search",
            "--indicator",
            "williams_r",
            "--symbol",
            "XAUUSD",
            "--timeframe",
            "M5",
            "--start",
            "2025-01-01",
            "--end",
            "2025-07-01",
            "--top",
            "10",
        ],
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 0
    assert stderr.getvalue() == ""
    assert (
        json.loads(stdout.getvalue())["specification_count"]
        == 7688
    )
    assert command.call["indicator_id"] == "williams_r"
    assert command.call["symbol"] == "XAUUSD"
    assert command.call["timeframe"] == "M5"
    assert command.call["top"] == 10
    assert command.call["metric"] == "net_profit"