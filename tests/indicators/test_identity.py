import pytest

from src.indicators.identity import IndicatorIdentity


def test_creates_identity() -> None:
    identity = IndicatorIdentity(
        id="williams_r",
        symbol="WILLR",
        name="Williams %R",
    )

    assert identity.id == "williams_r"
    assert identity.symbol == "WILLR"
    assert identity.name == "Williams %R"
    assert identity.version == 1


def test_rejects_empty_id() -> None:
    with pytest.raises(ValueError):
        IndicatorIdentity(
            id="",
            symbol="WILLR",
            name="Williams %R",
        )


def test_rejects_empty_symbol() -> None:
    with pytest.raises(ValueError):
        IndicatorIdentity(
            id="williams_r",
            symbol="",
            name="Williams %R",
        )


def test_rejects_empty_name() -> None:
    with pytest.raises(ValueError):
        IndicatorIdentity(
            id="williams_r",
            symbol="WILLR",
            name="",
        )