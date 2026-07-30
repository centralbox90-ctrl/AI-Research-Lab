from __future__ import annotations

import json

import pytest

from src.application.list_experiment_executions import (
    ListExperimentExecutions,
)
from src.cli.list_experiment_executions_command import (
    ListExperimentExecutionsCommand,
)


class StubExperimentExecutionCatalog:
    def __init__(
        self,
        execution_ids: tuple[str, ...],
    ) -> None:
        self.execution_ids = execution_ids
        self.calls = 0

    def list_execution_ids(
        self,
    ) -> tuple[str, ...]:
        self.calls += 1

        return self.execution_ids


def build_command(
    execution_ids: tuple[str, ...],
) -> tuple[
    ListExperimentExecutionsCommand,
    StubExperimentExecutionCatalog,
]:
    catalog = StubExperimentExecutionCatalog(
        execution_ids
    )
    application = ListExperimentExecutions(
        catalog=catalog
    )

    return (
        ListExperimentExecutionsCommand(
            application=application
        ),
        catalog,
    )


def test_renders_execution_id_list(
) -> None:
    command, catalog = build_command(
        (
            "execution-2",
            "execution-1",
        )
    )

    payload = json.loads(
        command.execute()
    )

    assert catalog.calls == 1
    assert payload["schema_version"] == 1
    assert payload["execution_count"] == 2
    assert payload["execution_ids"] == [
        "execution-1",
        "execution-2",
    ]


def test_renders_empty_execution_id_list(
) -> None:
    command, _ = build_command(())

    payload = json.loads(
        command.execute()
    )

    assert payload == {
        "schema_version": 1,
        "execution_count": 0,
        "execution_ids": [],
    }


def test_supports_compact_json(
) -> None:
    command, _ = build_command(
        ("execution-1",)
    )

    rendered = command.execute(
        indent=None
    )

    assert "\n" not in rendered
    assert json.loads(rendered)[
        "execution_count"
    ] == 1


def test_rejects_invalid_application(
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "application must be a "
            "ListExperimentExecutions"
        ),
    ):
        ListExperimentExecutionsCommand(
            application=object()
        )
