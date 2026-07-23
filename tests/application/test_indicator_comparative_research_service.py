from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import pandas as pd
import pytest

from src.application.canonical_market_dataset import (
    CanonicalMarketDataset,
)
from src.application.market_dataset_quality import (
    MarketDatasetQualityAnalyzer,
)
from src.application.indicator_comparative_research_design import (
    IndicatorComparativeResearchDesign,
)
from src.application.indicator_comparative_research_service import (
    IndicatorComparativeResearchService,
)
from src.application.indicator_research_result import (
    IndicatorResearchResult,
)
from src.research.market_dataset_fingerprint import (
    DatasetFingerprintContext,
    MarketDatasetCanonicalizer,
    MarketDatasetFingerprinter,
)
from src.research.outcome_specification import (
    ForwardReturnSpecification,
)
from src.research.specification import (
    IndicatorReference,
    ResearchSpecification,
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


class StubResearchExecutionService:
    def __init__(
        self,
        result: IndicatorResearchResult,
    ) -> None:
        self.result = result
        self.calls: list[
            tuple[pd.DataFrame, object]
        ] = []

    def execute(
        self,
        *,
        data: pd.DataFrame,
        specification: object,
    ) -> IndicatorResearchResult:
        self.calls.append(
            (
                data,
                specification,
            )
        )
        return self.result


def build_research_specification(
) -> ResearchSpecification:
    return ResearchSpecification.create(
        indicator=IndicatorReference(
            indicator_id="williams_r",
            indicator_version=1,
        ),
        output="williams_r",
        profile="overbought_oversold",
        observation_type="level_cross",
        calculation_parameters={
            "period": 14,
        },
        observation_parameters={
            "oversold_level": -80,
        },
    )


def build_design(
    *,
    research_specification=None,
    horizons: tuple[int, ...] = (1,),
    price_field: str = "close",
) -> IndicatorComparativeResearchDesign:
    return IndicatorComparativeResearchDesign(
        research_specification=(
            research_specification
            or build_research_specification()
        ),
        outcome_specification=(
            ForwardReturnSpecification(
                horizons=horizons,
                price_field=price_field,
            )
        ),
    )


def build_indicator_result(
    observations: tuple[int, ...] = (
        1,
        0,
        0,
        1,
        0,
    ),
) -> IndicatorResearchResult:
    series = StubSeries(
        (
            -85.0,
            -70.0,
            -50.0,
            -82.0,
            -40.0,
        )
    )

    return IndicatorResearchResult(
        research_specification=(
            build_research_specification()
        ),
        series=series,
        observations=observations,
        signal_result=SimpleNamespace(
            signals=tuple(
                object()
                for _ in observations
            ),
        ),
    )


def build_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "close": [
                100.0,
                110.0,
                120.0,
                130.0,
                140.0,
            ],
        }
    )


def build_dataset(
    data: pd.DataFrame | None = None,
) -> CanonicalMarketDataset:
    source = (
        build_data()
        if data is None
        else data.copy(deep=True)
    )
    close = source["close"].tolist()
    open_prices = (
        source["open"].tolist()
        if "open" in source.columns
        else close
    )

    canonical = (
        MarketDatasetCanonicalizer()
        .canonicalize(
            pd.DataFrame(
                {
                    "timestamp": pd.date_range(
                        "2026-01-01",
                        periods=len(source),
                        freq="h",
                        tz="UTC",
                    ),
                    "open": open_prices,
                    "high": [
                        max(open_price, close_price)
                        for open_price, close_price
                        in zip(open_prices, close)
                    ],
                    "low": [
                        min(open_price, close_price)
                        for open_price, close_price
                        in zip(open_prices, close)
                    ],
                    "close": close,
                    "tick_volume": [
                        100 + index
                        for index in range(len(source))
                    ],
                }
            )
        )
    )
    fingerprint = MarketDatasetFingerprinter().attach(
        canonical,
        DatasetFingerprintContext(
            symbol="EURUSD",
            timeframe="H1",
        ),
    )

    return CanonicalMarketDataset(
        data=canonical,
        fingerprint=fingerprint,
        quality_report=(
            MarketDatasetQualityAnalyzer().analyze(
                canonical
            )
        ),
    )


def test_runs_complete_indicator_comparative_pipeline(
) -> None:
    indicator_result = build_indicator_result()
    execution_service = (
        StubResearchExecutionService(
            indicator_result
        )
    )
    research_specification = (
        build_research_specification()
    )
    service = IndicatorComparativeResearchService(
        research_execution_service=(
            execution_service
        )
    )

    analysis = service.run(
        dataset=build_dataset(),
        design=build_design(
            research_specification=(
                research_specification
            ),
            horizons=(1, 2),
        ),
        symbol="EURUSD",
        timeframe="H1",
    )

    assert (
        analysis.candidate_result
        .observation_count
        == 1
    )
    assert (
        analysis.candidate_result
        .incomplete_observation_count
        == 1
    )
    assert (
        analysis.baseline_result
        .observation_count
        == 3
    )
    assert tuple(
        item.horizon
        for item in analysis.comparisons
    ) == (1, 2)

    assert len(execution_service.calls) == 1
    called_data, called_specification = (
        execution_service.calls[0]
    )
    assert called_specification is (
        research_specification
    )
    assert called_data.equals(build_dataset().data)


def test_rejects_noncanonical_dataset(
) -> None:
    service = IndicatorComparativeResearchService(
        research_execution_service=(
            StubResearchExecutionService(
                build_indicator_result()
            )
        )
    )

    with pytest.raises(
        TypeError,
        match=(
            "dataset must be a "
            "CanonicalMarketDataset"
        ),
    ):
        service.run(
            dataset=object(),
            design=build_design(),
            symbol="EURUSD",
            timeframe="H1",
        )


def test_preserves_materialized_observation_context(
) -> None:
    service = IndicatorComparativeResearchService(
        research_execution_service=(
            StubResearchExecutionService(
                build_indicator_result()
            )
        )
    )

    analysis = service.run(
        dataset=build_dataset(),
        design=build_design(
            horizons=(1,),
        ),
        symbol="EURUSD",
        timeframe="H1",
    )

    assert (
        analysis.candidate_result
        .observation_ids[0]
        == (
            f"{build_research_specification().fingerprint}:"
            "EURUSD:H1:0:1"
        )
    )


def test_uses_outcome_price_field() -> None:
    data = pd.DataFrame(
        {
            "open": [
                50.0,
                55.0,
                60.0,
                65.0,
                70.0,
            ],
            "close": [
                100.0,
                100.0,
                100.0,
                100.0,
                100.0,
            ],
        }
    )
    service = IndicatorComparativeResearchService(
        research_execution_service=(
            StubResearchExecutionService(
                build_indicator_result(
                    observations=(
                        1,
                        0,
                        0,
                        0,
                        0,
                    )
                )
            )
        )
    )

    analysis = service.run(
        dataset=build_dataset(data),
        design=build_design(
            horizons=(1,),
            price_field="open",
        ),
        symbol="EURUSD",
        timeframe="H1",
    )

    outcome = (
        analysis.candidate_result.outcomes[0]
    )

    assert outcome.start_price == 50.0
    assert outcome.end_price == 55.0


def test_rejects_result_without_complete_observations(
) -> None:
    service = IndicatorComparativeResearchService(
        research_execution_service=(
            StubResearchExecutionService(
                build_indicator_result(
                    observations=(
                        0,
                        0,
                        0,
                        1,
                        0,
                    )
                )
            )
        )
    )

    with pytest.raises(
        ValueError,
        match=(
            "candidate event study contains no "
            "complete observations"
        ),
    ):
        service.run(
            dataset=build_dataset(),
            design=build_design(
                horizons=(2,),
            ),
            symbol="EURUSD",
            timeframe="H1",
        )


def test_does_not_modify_data() -> None:
    dataset = build_dataset()
    original = dataset.data.copy(deep=True)
    service = IndicatorComparativeResearchService(
        research_execution_service=(
            StubResearchExecutionService(
                build_indicator_result()
            )
        )
    )

    service.run(
        dataset=dataset,
        design=build_design(
            horizons=(1,),
        ),
        symbol="EURUSD",
        timeframe="H1",
    )

    pd.testing.assert_frame_equal(
        dataset.data,
        original,
    )
