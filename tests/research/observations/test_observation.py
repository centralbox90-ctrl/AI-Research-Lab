from dataclasses import FrozenInstanceError
from datetime import UTC, datetime

import pytest

from src.research.observations.observation import Observation


def make_observation(**overrides: object) -> Observation:
    values: dict[str, object] = {
        "id": "observation-1",
        "definition_id": "rsi-oversold",
        "symbol": "EURUSD",
        "timeframe": "H1",
        "timestamp": datetime(2026, 1, 1, tzinfo=UTC),
        "bar_index": 42,
        "price": 1.125,
        "context": {
            "indicator_value": 28.5,
        },
    }
    values.update(overrides)
    return Observation(**values)


def test_observation_stores_event_data() -> None:
    timestamp = datetime(2026, 1, 1, tzinfo=UTC)

    observation = make_observation(timestamp=timestamp)

    assert observation.id == "observation-1"
    assert observation.definition_id == "rsi-oversold"
    assert observation.symbol == "EURUSD"
    assert observation.timeframe == "H1"
    assert observation.timestamp is timestamp
    assert observation.bar_index == 42
    assert observation.price == 1.125
    assert observation.context == {
        "indicator_value": 28.5,
    }


@pytest.mark.parametrize(
    ("field_name", "message"),
    [
        ("id", "id must not be empty"),
        ("definition_id", "definition_id must not be empty"),
        ("symbol", "symbol must not be empty"),
        ("timeframe", "timeframe must not be empty"),
    ],
)
@pytest.mark.parametrize("blank_value", ["", " ", "\t", "\n"])
def test_observation_rejects_blank_required_text(
    field_name: str,
    message: str,
    blank_value: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        make_observation(**{field_name: blank_value})


def test_observation_rejects_negative_bar_index() -> None:
    with pytest.raises(
        ValueError,
        match="bar_index must be greater than or equal to zero",
    ):
        make_observation(bar_index=-1)


def test_observation_accepts_zero_bar_index() -> None:
    observation = make_observation(bar_index=0)

    assert observation.bar_index == 0


def test_observation_defaults_to_empty_context() -> None:
    observation = Observation(
        id="observation-1",
        definition_id="rsi-oversold",
        symbol="EURUSD",
        timeframe="H1",
        timestamp=datetime(2026, 1, 1, tzinfo=UTC),
        bar_index=0,
        price=1.125,
    )

    assert observation.context == {}


def test_observation_fields_are_frozen() -> None:
    observation = make_observation()

    with pytest.raises(FrozenInstanceError):
        observation.price = 1.2
