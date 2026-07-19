from __future__ import annotations

import pytest

from src.indicators.catalog import (
    DuplicateIndicatorError,
    IndicatorCatalog,
    IndicatorNotFoundError,
)
from src.indicators.descriptor import IndicatorDescriptor


def create_indicator(
    indicator_id: str,
) -> IndicatorDescriptor:
    def calculator(data, specification):
        raise NotImplementedError

    return IndicatorDescriptor(
        id=indicator_id,
        symbol=indicator_id.upper(),
        name=indicator_id.title(),
        version=1,
        calculator=calculator,
        default_parameters={},
    )


def test_catalog_contains_indicators() -> None:
    first = create_indicator("first")
    second = create_indicator("second")

    catalog = IndicatorCatalog(
        [
            first,
            second,
        ]
    )

    assert len(catalog) == 2
    assert catalog.contains("first")
    assert catalog.contains("second")
    assert not catalog.contains("missing")


def test_catalog_returns_indicator_by_id() -> None:
    indicator = create_indicator("first")
    catalog = IndicatorCatalog([indicator])

    assert catalog.get("first") is indicator


def test_catalog_exposes_ids() -> None:
    catalog = IndicatorCatalog(
        [
            create_indicator("first"),
            create_indicator("second"),
        ]
    )

    assert catalog.ids == (
        "first",
        "second",
    )


def test_catalog_is_iterable() -> None:
    first = create_indicator("first")
    second = create_indicator("second")

    catalog = IndicatorCatalog(
        [
            first,
            second,
        ]
    )

    assert tuple(catalog) == (
        first,
        second,
    )


def test_catalog_rejects_duplicate_ids() -> None:
    first = create_indicator("duplicate")
    second = create_indicator("duplicate")

    with pytest.raises(
        DuplicateIndicatorError,
        match="Duplicate indicator id 'duplicate'",
    ):
        IndicatorCatalog(
            [
                first,
                second,
            ]
        )


def test_catalog_rejects_unknown_indicator() -> None:
    catalog = IndicatorCatalog([])

    with pytest.raises(
        IndicatorNotFoundError,
        match="Unknown indicator 'missing'",
    ):
        catalog.get("missing")