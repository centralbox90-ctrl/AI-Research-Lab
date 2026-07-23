from dataclasses import FrozenInstanceError

import pytest

from src.research.outcome_specification import (
    ForwardReturnSpecification,
)


def test_stores_normalized_forward_return_definition() -> None:
    specification = ForwardReturnSpecification(
        horizons=(10, 1, 5),
        price_field="  close  ",
    )

    assert specification.horizons == (1, 5, 10)
    assert specification.price_field == "close"


def test_uses_close_as_default_price_field() -> None:
    specification = ForwardReturnSpecification(
        horizons=(1,),
    )

    assert specification.price_field == "close"


def test_rejects_empty_horizons() -> None:
    with pytest.raises(
        ValueError,
        match="horizons must not be empty",
    ):
        ForwardReturnSpecification(horizons=())


@pytest.mark.parametrize(
    "horizon",
    [
        0,
        -1,
        -10,
    ],
)
def test_rejects_non_positive_horizons(
    horizon: int,
) -> None:
    with pytest.raises(
        ValueError,
        match="each horizon must be positive",
    ):
        ForwardReturnSpecification(
            horizons=(horizon,),
        )


@pytest.mark.parametrize(
    "horizon",
    [
        True,
        False,
        1.0,
        "1",
        None,
    ],
)
def test_rejects_non_integer_horizons(
    horizon: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="each horizon must be an integer",
    ):
        ForwardReturnSpecification(
            horizons=(horizon,),
        )


def test_rejects_non_tuple_horizons() -> None:
    with pytest.raises(
        TypeError,
        match="horizons must be a tuple",
    ):
        ForwardReturnSpecification(
            horizons=[1, 5, 10],
        )


def test_rejects_duplicate_horizons() -> None:
    with pytest.raises(
        ValueError,
        match="horizons must not contain duplicates",
    ):
        ForwardReturnSpecification(
            horizons=(1, 5, 1),
        )


@pytest.mark.parametrize(
    "price_field",
    [
        "",
        " ",
        "\t",
        "\n",
    ],
)
def test_rejects_blank_price_field(
    price_field: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="price_field must not be empty",
    ):
        ForwardReturnSpecification(
            horizons=(1,),
            price_field=price_field,
        )


def test_is_immutable() -> None:
    specification = ForwardReturnSpecification(
        horizons=(1, 5, 10),
    )

    with pytest.raises(FrozenInstanceError):
        specification.price_field = "open"
