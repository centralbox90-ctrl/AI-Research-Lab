from dataclasses import FrozenInstanceError

import pytest

from src.application.indicator_comparative_research_result import (
    IndicatorComparativeResearchResult,
)
from src.application.market_dataset_quality import (
    DataQualityReport,
)
from src.indicators.implementations.rsi import INDICATOR
from src.research.comparative_analysis import (
    ComparativeAnalysis,
)
from src.research.market_dataset_fingerprint import (
    MarketDatasetFingerprint,
)
from src.research.specification_factory import (
    create_default_research_specification,
)


def build_dataset_fingerprint(
) -> MarketDatasetFingerprint:
    return MarketDatasetFingerprint(
        content_fingerprint="content-fingerprint",
        dataset_fingerprint="dataset-fingerprint",
        algorithm="sha256",
        content_schema_version="content-v1",
        dataset_schema_version="dataset-v1",
        normalization_schema_version=(
            "normalization-v1"
        ),
    )


def build_quality_report() -> DataQualityReport:
    return DataQualityReport(
        row_count=100,
        first_timestamp=1_700_000_000_000_000_000,
        last_timestamp=1_700_356_400_000_000_000,
        duplicate_timestamp_count=0,
        missing_timestamp_count=0,
        invalid_ohlc_count=0,
        monotonic_timestamp=True,
    )


def build_result(
    **overrides: object,
) -> IndicatorComparativeResearchResult:
    arguments = {
        "indicator_id": "  rsi  ",
        "symbol": " eurusd ",
        "timeframe": " h1 ",
        "research_specification": (
            create_default_research_specification(
                INDICATOR
            )
        ),
        "dataset_fingerprint": (
            build_dataset_fingerprint()
        ),
        "data_quality_report": (
            build_quality_report()
        ),
        "analysis": object.__new__(
            ComparativeAnalysis
        ),
    }
    arguments.update(overrides)

    return IndicatorComparativeResearchResult(
        **arguments
    )


def test_builds_reproducible_comparative_result(
) -> None:
    result = build_result()

    assert result.indicator_id == "rsi"
    assert result.symbol == "EURUSD"
    assert result.timeframe == "H1"
    assert result.research_fingerprint == (
        result.research_specification.fingerprint
    )
    assert result.dataset_id == "dataset-fingerprint"
    assert result.data_quality_report.row_count == 100


def test_is_immutable() -> None:
    result = build_result()

    with pytest.raises(FrozenInstanceError):
        result.symbol = "GBPUSD"


@pytest.mark.parametrize(
    ("field_name", "invalid_value", "error_type", "message"),
    (
        (
            "indicator_id",
            object(),
            TypeError,
            "indicator_id must be a string",
        ),
        (
            "indicator_id",
            "   ",
            ValueError,
            "indicator_id must not be empty",
        ),
        (
            "symbol",
            object(),
            TypeError,
            "symbol must be a string",
        ),
        (
            "timeframe",
            "   ",
            ValueError,
            "timeframe must not be empty",
        ),
        (
            "research_specification",
            object(),
            TypeError,
            "research_specification must be a "
            "ResearchSpecification",
        ),
        (
            "dataset_fingerprint",
            object(),
            TypeError,
            "dataset_fingerprint must be a "
            "MarketDatasetFingerprint",
        ),
        (
            "data_quality_report",
            object(),
            TypeError,
            "data_quality_report must be a "
            "DataQualityReport",
        ),
        (
            "analysis",
            object(),
            TypeError,
            "analysis must be a ComparativeAnalysis",
        ),
    ),
)
def test_rejects_invalid_arguments(
    field_name: str,
    invalid_value: object,
    error_type: type[Exception],
    message: str,
) -> None:
    with pytest.raises(
        error_type,
        match=message,
    ):
        build_result(
            **{field_name: invalid_value}
        )


def test_rejects_indicator_identity_mismatch(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "indicator_id must match the "
            "research specification"
        ),
    ):
        build_result(
            indicator_id="williams_r"
        )
