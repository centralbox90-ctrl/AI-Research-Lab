from dataclasses import FrozenInstanceError

import pytest

from src.research.assumption import (
    Assumption,
    AssumptionSet,
    AssumptionStatus,
    AssumptionType,
)


def create_execution_assumption(
    assumption_id: str = "execution.slippage",
) -> Assumption:
    return Assumption(
        id=assumption_id,
        type=AssumptionType.EXECUTION,
        statement="Slippage is always adverse.",
        value={
            "model": "deterministic_percent",
            "percent": 0.05,
        },
        scope=(
            "market_backtest",
            "all_position_sides",
        ),
    )


def test_assumption_is_immutable() -> None:
    assumption = create_execution_assumption()

    with pytest.raises(FrozenInstanceError):
        assumption.version = 2


def test_assumption_set_returns_assumption_by_id() -> None:
    assumption = create_execution_assumption()

    assumption_set = AssumptionSet(
        id="execution-assumptions-v1",
        assumptions=(assumption,),
    )

    assert assumption_set.get(
        "execution.slippage"
    ) == assumption


def test_assumption_set_rejects_duplicate_ids() -> None:
    first = create_execution_assumption()
    second = create_execution_assumption()

    with pytest.raises(
        ValueError,
        match="assumption ids must be unique",
    ):
        AssumptionSet(
            id="invalid-set",
            assumptions=(first, second),
        )


def test_changed_assumption_supersedes_previous_version() -> None:
    previous = create_execution_assumption()

    current = Assumption(
        id="execution.slippage.v2",
        type=AssumptionType.EXECUTION,
        statement="Slippage is adverse and deterministic.",
        value={
            "model": "deterministic_percent",
            "percent": 0.10,
        },
        version=2,
        status=AssumptionStatus.ACTIVE,
        supersedes_assumption_id=previous.id,
    )

    assert current.version == 2
    assert current.supersedes_assumption_id == previous.id
