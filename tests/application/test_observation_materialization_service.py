from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import pandas as pd
import pytest

from src.application.indicator_research_result import (
    IndicatorResearchResult,
)
from src.application.observation_materialization_service import (
    ObservationMaterializationService,
)


class StubSeries:
    def __init__(
        self,
        values: tuple[float | None, ...],
    ) -> None:
        self.values = values
        self.timestamps = tuple(
            datetime(
                2026,
                1,
                1,
                tzinfo=UTC,
            )
            + timedelta(hours=index)
            for index in range(len(values))
        )

    def __len__(self) -> int:
        return len(self.values)

    def value_at(
        self,
        index: int,
    ) -> float | None:
        return self.values[index]

    def timestamp_at(
        self,
        index: int,
    ) -> datetime:
        return self.timestamps[index]


def build_result(
    observations: tuple[int, ...] = (
        1,
        0,
        -1,
    ),
) -> IndicatorResearchResult:
    series = StubSeries(
        (
            -85.0,
            -50.0,
            -15.0,
        )
    )

    return IndicatorResearchResult(
        research_specification=SimpleNamespace(
            fingerprint="research-fingerprint",
            indicator=SimpleNamespace(
                indicator_id="williams_r",
            ),
            output="williams_r",
        ),
        series=series,
        observations=observations,
        signal_result=SimpleNamespace(
            signals=(
                object(),
                object(),
                object(),
            ),
        ),
    )


def build_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "close": [
                100.0,
                101.0,
                102.0,
            ],
        }
    )


def test_materializes_nonzero_observations(
) -> None:
    observations = (
        ObservationMaterializationService()
        .materialize(
            data=build_data(),
            result=build_result(),
            symbol="  EURUSD  ",
            timeframe="  H1  ",
        )
    )

    assert tuple(
        observation.bar_index
        for observation in observations
    ) == (0, 2)
    assert tuple(
        observation.price
        for observation in observations
    ) == (100.0, 102.0)
    assert tuple(
        observation.context[
            "observation_signal"
        ]
        for observation in observations
    ) == (1, -1)

    first = observations[0]

    assert first.definition_id == (
        "research-fingerprint"
    )
    assert first.symbol == "EURUSD"
    assert first.timeframe == "H1"
    assert first.context["indicator_id"] == (
        "williams_r"
    )
    assert first.context["indicator_output"] == (
        "williams_r"
    )
    assert first.context["indicator_value"] == (
        -85.0
    )
    assert first.id == (
        "research-fingerprint:"
        "EURUSD:H1:0:1"
    )


def test_returns_empty_tuple_without_events(
) -> None:
    observations = (
        ObservationMaterializationService()
        .materialize(
            data=build_data(),
            result=build_result(
                observations=(0, 0, 0)
            ),
            symbol="EURUSD",
            timeframe="H1",
        )
    )

    assert observations == ()


def test_uses_configured_price_field() -> None:
    data = pd.DataFrame(
        {
            "open": [
                50.0,
                51.0,
                52.0,
            ],
        }
    )

    observations = (
        ObservationMaterializationService()
        .materialize(
            data=data,
            result=build_result(),
            symbol="EURUSD",
            timeframe="H1",
            price_field="open",
        )
    )

    assert observations[0].price == 50.0


@pytest.mark.parametrize(
    ("field_name", "invalid_value", "message"),
    (
        (
            "data",
            object(),
            "data must be a pandas DataFrame",
        ),
        (
            "result",
            object(),
            (
                "result must be an "
                "IndicatorResearchResult"
            ),
        ),
        (
            "symbol",
            object(),
            "symbol must be a string",
        ),
        (
            "timeframe",
            object(),
            "timeframe must be a string",
        ),
        (
            "price_field",
            object(),
            "price_field must be a string",
        ),
    ),
)
def test_rejects_invalid_arguments(
    field_name: str,
    invalid_value: object,
    message: str,
) -> None:
    arguments = {
        "data": build_data(),
        "result": build_result(),
        "symbol": "EURUSD",
        "timeframe": "H1",
        "price_field": "close",
    }
    arguments[field_name] = invalid_value

    with pytest.raises(
        TypeError,
        match=message,
    ):
        (
            ObservationMaterializationService()
            .materialize(**arguments)
        )


@pytest.mark.parametrize(
    "field_name",
    (
        "symbol",
        "timeframe",
        "price_field",
    ),
)
def test_rejects_empty_text_arguments(
    field_name: str,
) -> None:
    arguments = {
        "data": build_data(),
        "result": build_result(),
        "symbol": "EURUSD",
        "timeframe": "H1",
        "price_field": "close",
    }
    arguments[field_name] = "   "

    with pytest.raises(
        ValueError,
        match=f"{field_name} must not be empty",
    ):
        (
            ObservationMaterializationService()
            .materialize(**arguments)
        )


def test_rejects_data_series_length_mismatch(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "data and indicator series must have "
            "equal length"
        ),
    ):
        (
            ObservationMaterializationService()
            .materialize(
                data=pd.DataFrame(
                    {
                        "close": [
                            100.0,
                            101.0,
                        ],
                    }
                ),
                result=build_result(),
                symbol="EURUSD",
                timeframe="H1",
            )
        )


def test_rejects_missing_price_field() -> None:
    with pytest.raises(
        ValueError,
        match="data is missing price field 'close'",
    ):
        (
            ObservationMaterializationService()
            .materialize(
                data=pd.DataFrame(
                    {
                        "open": [
                            100.0,
                            101.0,
                            102.0,
                        ],
                    }
                ),
                result=build_result(),
                symbol="EURUSD",
                timeframe="H1",
            )
        )


def test_does_not_modify_data() -> None:
    data = build_data()
    original = data.copy(deep=True)

    ObservationMaterializationService().materialize(
        data=data,
        result=build_result(),
        symbol="EURUSD",
        timeframe="H1",
    )

    pd.testing.assert_frame_equal(
        data,
        original,
    )
