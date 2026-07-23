from datetime import UTC, datetime

import pandas as pd
import pytest

from src.research.forward_outcome_calculator import (
    ForwardOutcomeCalculator,
)
from src.research.observations.observation import (
    Observation,
)
from src.research.outcome_specification import (
    ForwardReturnSpecification,
)


def build_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "timestamp": range(6),
            "open": [
                99.0,
                100.0,
                101.0,
                102.0,
                103.0,
                104.0,
            ],
            "high": [
                101.0,
                102.0,
                103.0,
                104.0,
                105.0,
                106.0,
            ],
            "low": [
                98.0,
                99.0,
                100.0,
                101.0,
                102.0,
                103.0,
            ],
            "close": [
                100.0,
                102.0,
                104.0,
                106.0,
                108.0,
                110.0,
            ],
            "tick_volume": [
                10,
                11,
                12,
                13,
                14,
                15,
            ],
        }
    )


def build_observation(
    *,
    bar_index: int = 1,
) -> Observation:
    return Observation(
        id="observation-1",
        definition_id="rsi-oversold",
        symbol="EURUSD",
        timeframe="H1",
        timestamp=datetime(
            2026,
            1,
            1,
            tzinfo=UTC,
        ),
        bar_index=bar_index,
        price=102.0,
    )


def test_calculates_requested_forward_returns() -> None:
    results = ForwardOutcomeCalculator().calculate(
        data=build_data(),
        observation=build_observation(),
        specification=ForwardReturnSpecification(
            horizons=(1, 3),
        ),
    )

    assert tuple(
        result.horizon
        for result in results
    ) == (1, 3)

    assert all(
        result.observation_id == "observation-1"
        for result in results
    )

    assert results[0].start_bar_index == 1
    assert results[0].end_bar_index == 2
    assert results[0].value == pytest.approx(
        (104.0 / 102.0) - 1.0
    )

    assert results[1].end_bar_index == 4
    assert results[1].value == pytest.approx(
        (108.0 / 102.0) - 1.0
    )


def test_uses_configured_price_field() -> None:
    result = ForwardOutcomeCalculator().calculate(
        data=build_data(),
        observation=build_observation(),
        specification=ForwardReturnSpecification(
            horizons=(1,),
            price_field="open",
        ),
    )[0]

    assert result.start_price == 100.0
    assert result.end_price == 101.0


def test_does_not_mutate_data() -> None:
    data = build_data()
    original = data.copy(deep=True)

    ForwardOutcomeCalculator().calculate(
        data=data,
        observation=build_observation(),
        specification=ForwardReturnSpecification(
            horizons=(1,),
        ),
    )

    pd.testing.assert_frame_equal(data, original)


@pytest.mark.parametrize(
    ("argument", "value", "message"),
    [
        (
            "data",
            object(),
            "data must be a pandas DataFrame",
        ),
        (
            "observation",
            object(),
            "observation must be an Observation",
        ),
        (
            "specification",
            object(),
            "specification must be a",
        ),
    ],
)
def test_rejects_invalid_argument_types(
    argument: str,
    value: object,
    message: str,
) -> None:
    arguments: dict[str, object] = {
        "data": build_data(),
        "observation": build_observation(),
        "specification": (
            ForwardReturnSpecification(
                horizons=(1,),
            )
        ),
    }
    arguments[argument] = value

    with pytest.raises(
        TypeError,
        match=message,
    ):
        ForwardOutcomeCalculator().calculate(
            **arguments
        )


def test_rejects_empty_data() -> None:
    with pytest.raises(
        ValueError,
        match="data must not be empty",
    ):
        ForwardOutcomeCalculator().calculate(
            data=pd.DataFrame(),
            observation=build_observation(),
            specification=ForwardReturnSpecification(
                horizons=(1,),
            ),
        )


def test_rejects_missing_price_field() -> None:
    with pytest.raises(
        ValueError,
        match="data is missing price field 'median'",
    ):
        ForwardOutcomeCalculator().calculate(
            data=build_data(),
            observation=build_observation(),
            specification=ForwardReturnSpecification(
                horizons=(1,),
                price_field="median",
            ),
        )


def test_rejects_observation_outside_data() -> None:
    with pytest.raises(
        ValueError,
        match="observation bar_index is outside data",
    ):
        ForwardOutcomeCalculator().calculate(
            data=build_data(),
            observation=build_observation(
                bar_index=6,
            ),
            specification=ForwardReturnSpecification(
                horizons=(1,),
            ),
        )


def test_rejects_incomplete_forward_horizon() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "data does not contain all requested "
            "forward horizons"
        ),
    ):
        ForwardOutcomeCalculator().calculate(
            data=build_data(),
            observation=build_observation(
                bar_index=4,
            ),
            specification=ForwardReturnSpecification(
                horizons=(2,),
            ),
        )
