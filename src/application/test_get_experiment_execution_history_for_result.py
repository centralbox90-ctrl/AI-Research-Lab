from __future__ import annotations

from datetime import UTC, datetime

import pytest

from src.application.get_experiment_execution_history_for_result import (
    GetExperimentExecutionHistoryForResult,
)
from src.research.experiment_execution import (
    ExperimentExecution,
)


class StubExecutionLister:
    def __init__(
        self,
        execution_ids: tuple[str, ...],
    ) -> None:
        self.execution_ids = execution_ids
        self.calls = 0

    def execute(self) -> tuple[str, ...]:
        self.calls += 1
        return self.execution_ids


class StubHistoryGetter:
    def __init__(
        self,
        histories: dict[
            str,
            tuple[ExperimentExecution, ...],
        ],
    ) -> None:
        self.histories = histories
        self.calls: list[str] = []

    def execute(
        self,
        execution_id: str,
    ) -> tuple[ExperimentExecution, ...]:
        self.calls.append(execution_id)
        return self.histories.get(
            execution_id,
            (),
        )


def build_history(
    *,
    execution_id: str,
    result_id: str,
) -> tuple[ExperimentExecution, ...]:
    pending = ExperimentExecution(
        execution_id=execution_id,
        experiment_id="experiment-momentum",
        specification_fingerprint="a" * 64,
        correlation_id="research-cycle-1",
        created_at=datetime(
            2026,
            8,
            2,
            10,
            0,
            tzinfo=UTC,
        ),
    )
    running = pending.start(
        environment_fingerprint="b" * 64,
        started_at=datetime(
            2026,
            8,
            2,
            10,
            1,
            tzinfo=UTC,
        ),
    )
    succeeded = running.succeed(
        result_id=result_id,
        finished_at=datetime(
            2026,
            8,
            2,
            10,
            2,
            tzinfo=UTC,
        ),
    )

    return (
        pending,
        running,
        succeeded,
    )


def test_returns_history_matching_result_id(
) -> None:
    execution_lister = StubExecutionLister(
        (
            "execution-1",
            "execution-2",
        )
    )
    history_getter = StubHistoryGetter(
        {
            "execution-1": build_history(
                execution_id="execution-1",
                result_id="result-1",
            ),
            "execution-2": build_history(
                execution_id="execution-2",
                result_id="result-2",
            ),
        }
    )
    use_case = (
        GetExperimentExecutionHistoryForResult(
            execution_lister=execution_lister,
            history_getter=history_getter,
        )
    )

    history = use_case.execute(
        "  result-2  "
    )

    assert history[-1].result_id == "result-2"
    assert history[-1].status.value == "SUCCEEDED"
    assert execution_lister.calls == 1
    assert history_getter.calls == [
        "execution-1",
        "execution-2",
    ]


def test_returns_empty_history_when_result_is_missing(
) -> None:
    use_case = (
        GetExperimentExecutionHistoryForResult(
            execution_lister=StubExecutionLister(
                ("execution-1",)
            ),
            history_getter=StubHistoryGetter(
                {
                    "execution-1": build_history(
                        execution_id="execution-1",
                        result_id="result-1",
                    ),
                }
            ),
        )
    )

    assert use_case.execute(
        "result-missing"
    ) == ()


def test_rejects_duplicate_result_references(
) -> None:
    use_case = (
        GetExperimentExecutionHistoryForResult(
            execution_lister=StubExecutionLister(
                (
                    "execution-1",
                    "execution-2",
                )
            ),
            history_getter=StubHistoryGetter(
                {
                    "execution-1": build_history(
                        execution_id="execution-1",
                        result_id="result-shared",
                    ),
                    "execution-2": build_history(
                        execution_id="execution-2",
                        result_id="result-shared",
                    ),
                }
            ),
        )
    )

    with pytest.raises(
        ValueError,
        match=(
            "multiple execution histories reference "
            "result_id: result-shared"
        ),
    ):
        use_case.execute("result-shared")


@pytest.mark.parametrize(
    "result_id, error_type, message",
    [
        (
            None,
            TypeError,
            "result_id must be a string",
        ),
        (
            "   ",
            ValueError,
            "result_id must not be empty",
        ),
    ],
)
def test_rejects_invalid_result_id(
    result_id: object,
    error_type: type[Exception],
    message: str,
) -> None:
    use_case = (
        GetExperimentExecutionHistoryForResult(
            execution_lister=StubExecutionLister(
                ()
            ),
            history_getter=StubHistoryGetter(
                {}
            ),
        )
    )

    with pytest.raises(
        error_type,
        match=message,
    ):
        use_case.execute(result_id)


def test_rejects_invalid_collaborators(
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "execution_lister must provide execute"
        ),
    ):
        GetExperimentExecutionHistoryForResult(
            execution_lister=object(),
            history_getter=StubHistoryGetter(
                {}
            ),
        )

    with pytest.raises(
        TypeError,
        match=(
            "history_getter must provide execute"
        ),
    ):
        GetExperimentExecutionHistoryForResult(
            execution_lister=StubExecutionLister(
                ()
            ),
            history_getter=object(),
        )
