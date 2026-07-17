from datetime import datetime, timezone

from src.research import (
    Assumption,
    AssumptionSet,
    AssumptionType,
)


def create_assumption(
    assumption_id: str,
    value,
    created_at: datetime,
) -> Assumption:
    return Assumption(
        id=assumption_id,
        type=AssumptionType.EXECUTION,
        statement=f"Assumption {assumption_id}",
        value=value,
        created_at=created_at,
    )


def test_fingerprint_is_independent_of_assumption_order() -> None:
    created_at = datetime(
        2026,
        1,
        1,
        tzinfo=timezone.utc,
    )

    first = create_assumption(
        "execution.first",
        1,
        created_at,
    )
    second = create_assumption(
        "execution.second",
        2,
        created_at,
    )

    left = AssumptionSet(
        id="left",
        assumptions=(first, second),
    )
    right = AssumptionSet(
        id="right",
        assumptions=(second, first),
    )

    assert left.fingerprint() == right.fingerprint()


def test_fingerprint_ignores_creation_timestamps() -> None:
    first = create_assumption(
        "execution.slippage",
        0.05,
        datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    second = create_assumption(
        "execution.slippage",
        0.05,
        datetime(2026, 2, 1, tzinfo=timezone.utc),
    )

    left = AssumptionSet(
        id="left",
        assumptions=(first,),
        created_at=datetime(
            2026,
            3,
            1,
            tzinfo=timezone.utc,
        ),
    )
    right = AssumptionSet(
        id="right",
        assumptions=(second,),
        created_at=datetime(
            2026,
            4,
            1,
            tzinfo=timezone.utc,
        ),
    )

    assert left.fingerprint() == right.fingerprint()


def test_fingerprint_is_independent_of_dict_key_order() -> None:
    created_at = datetime(
        2026,
        1,
        1,
        tzinfo=timezone.utc,
    )

    first = create_assumption(
        "execution.model",
        {
            "percent": 0.05,
            "model": "deterministic",
        },
        created_at,
    )
    second = create_assumption(
        "execution.model",
        {
            "model": "deterministic",
            "percent": 0.05,
        },
        created_at,
    )

    left = AssumptionSet(
        id="left",
        assumptions=(first,),
    )
    right = AssumptionSet(
        id="right",
        assumptions=(second,),
    )

    assert left.fingerprint() == right.fingerprint()


def test_fingerprint_changes_when_value_changes() -> None:
    created_at = datetime(
        2026,
        1,
        1,
        tzinfo=timezone.utc,
    )

    first = create_assumption(
        "execution.slippage",
        0.05,
        created_at,
    )
    second = create_assumption(
        "execution.slippage",
        0.10,
        created_at,
    )

    left = AssumptionSet(
        id="left",
        assumptions=(first,),
    )
    right = AssumptionSet(
        id="right",
        assumptions=(second,),
    )

    assert left.fingerprint() != right.fingerprint()


def test_fingerprint_has_sha256_format() -> None:
    assumption_set = AssumptionSet(
        id="set",
        assumptions=(
            create_assumption(
                "execution.slippage",
                0.05,
                datetime(
                    2026,
                    1,
                    1,
                    tzinfo=timezone.utc,
                ),
            ),
        ),
    )

    fingerprint = assumption_set.fingerprint()

    assert len(fingerprint) == 64
    assert all(
        character in "0123456789abcdef"
        for character in fingerprint
    )
