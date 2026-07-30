from __future__ import annotations

import pytest

from src.application.list_experiment_executions import (
    ListExperimentExecutions,
)


class StubExperimentExecutionCatalog:
    def __init__(
        self,
        execution_ids: object,
    ) -> None:
        self.execution_ids = execution_ids
        self.calls = 0

    def list_execution_ids(
        self,
    ) -> object:
        self.calls += 1

        return self.execution_ids


def test_lists_normalized_execution_ids_deterministically(
) -> None:
    catalog = StubExperimentExecutionCatalog(
        (
            " execution-2 ",
            "execution-1",
        )
    )
    use_case = ListExperimentExecutions(
        catalog=catalog
    )

    assert use_case.execute() == (
        "execution-1",
        "execution-2",
    )
    assert catalog.calls == 1


def test_returns_empty_tuple(
) -> None:
    catalog = StubExperimentExecutionCatalog(
        ()
    )

    assert ListExperimentExecutions(
        catalog=catalog
    ).execute() == ()


def test_rejects_catalog_without_listing(
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "catalog must provide "
            "list_execution_ids"
        ),
    ):
        ListExperimentExecutions(
            catalog=object()
        )


def test_rejects_non_tuple_result(
) -> None:
    use_case = ListExperimentExecutions(
        catalog=(
            StubExperimentExecutionCatalog(
                []
            )
        )
    )

    with pytest.raises(
        TypeError,
        match="execution IDs must be a tuple",
    ):
        use_case.execute()


def test_rejects_non_string_execution_id(
) -> None:
    use_case = ListExperimentExecutions(
        catalog=(
            StubExperimentExecutionCatalog(
                (object(),)
            )
        )
    )

    with pytest.raises(
        TypeError,
        match=(
            "each execution ID must be a string"
        ),
    ):
        use_case.execute()


def test_rejects_empty_execution_id(
) -> None:
    use_case = ListExperimentExecutions(
        catalog=(
            StubExperimentExecutionCatalog(
                ("   ",)
            )
        )
    )

    with pytest.raises(
        ValueError,
        match=(
            "execution ID must not be empty"
        ),
    ):
        use_case.execute()


def test_rejects_duplicate_normalized_ids(
) -> None:
    use_case = ListExperimentExecutions(
        catalog=(
            StubExperimentExecutionCatalog(
                (
                    "execution-1",
                    " execution-1 ",
                )
            )
        )
    )

    with pytest.raises(
        ValueError,
        match=(
            "execution IDs must be unique"
        ),
    ):
        use_case.execute()
