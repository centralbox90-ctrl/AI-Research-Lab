from math import inf
from typing import Any

import pytest

from src.application.compare_indicator_comparative_research_artifacts import (
    CompareIndicatorComparativeResearchArtifacts,
)


def build_artifact(
    *,
    research_fingerprint: str = "research-a",
    dataset_id: str = "dataset-a",
    indicator_id: str = "rsi",
    symbol: str = "EURUSD",
    timeframe: str = "H1",
    price_field: str = "close",
    horizons: tuple[int, ...] = (3, 1),
    metric_shift: float = 0.0,
) -> dict[str, Any]:
    return {
        "artifact_type": (
            "indicator_comparative_research"
        ),
        "artifact_version": 1,
        "indicator": {
            "id": indicator_id,
            "research_fingerprint": (
                research_fingerprint
            ),
        },
        "market": {
            "symbol": symbol,
            "timeframe": timeframe,
        },
        "dataset": {
            "id": dataset_id,
        },
        "outcome_specification": {
            "horizons": list(horizons),
            "price_field": price_field,
        },
        "analysis": {
            "comparisons": [
                {
                    "horizon": horizon,
                    "mean_return_difference": (
                        horizon * 0.01
                        + metric_shift
                    ),
                    "median_return_difference": (
                        horizon * 0.02
                        + metric_shift
                    ),
                    "positive_rate_difference": (
                        horizon * 0.03
                        + metric_shift
                    ),
                }
                for horizon in horizons
            ],
        },
    }


def test_compares_horizon_effects() -> None:
    artifact_a = build_artifact()
    artifact_b = build_artifact(
        research_fingerprint="research-b",
        dataset_id="dataset-b",
        metric_shift=0.05,
    )

    comparison = (
        CompareIndicatorComparativeResearchArtifacts()
        .execute(
            artifact_a,
            artifact_b,
        )
    )

    assert comparison["artifact_type"] == (
        "indicator_comparative_research_comparison"
    )
    assert comparison["artifact_version"] == 1
    assert comparison["artifact_a"] == {
        "research_fingerprint": "research-a",
        "dataset_id": "dataset-a",
    }
    assert comparison["artifact_b"] == {
        "research_fingerprint": "research-b",
        "dataset_id": "dataset-b",
    }
    assert comparison["indicator"] == {
        "id": "rsi",
    }
    assert comparison["market"] == {
        "symbol": "EURUSD",
        "timeframe": "H1",
    }
    assert comparison[
        "outcome_specification"
    ] == {
        "horizons": [1, 3],
        "price_field": "close",
    }

    deltas = comparison["horizon_deltas"]

    assert isinstance(deltas, list)
    assert [
        delta["horizon"]
        for delta in deltas
    ] == [1, 3]

    for delta in deltas:
        assert delta[
            "mean_return_difference_delta"
        ] == pytest.approx(0.05)
        assert delta[
            "median_return_difference_delta"
        ] == pytest.approx(0.05)
        assert delta[
            "positive_rate_difference_delta"
        ] == pytest.approx(0.05)


@pytest.mark.parametrize(
    (
        "section_name",
        "field_name",
        "value",
        "message",
    ),
    [
        (
            "indicator",
            "id",
            "williams_r",
            "same indicator id",
        ),
        (
            "market",
            "symbol",
            "GBPUSD",
            "same symbol",
        ),
        (
            "market",
            "timeframe",
            "M15",
            "same timeframe",
        ),
        (
            "outcome_specification",
            "price_field",
            "open",
            "same price field",
        ),
    ],
)
def test_rejects_incompatible_identity(
    section_name: str,
    field_name: str,
    value: str,
    message: str,
) -> None:
    artifact_a = build_artifact()
    artifact_b = build_artifact()
    section = artifact_b[section_name]

    assert isinstance(section, dict)

    section[field_name] = value

    with pytest.raises(
        ValueError,
        match=message,
    ):
        (
            CompareIndicatorComparativeResearchArtifacts()
            .execute(
                artifact_a,
                artifact_b,
            )
        )


def test_rejects_different_horizons() -> None:
    artifact_a = build_artifact(
        horizons=(1, 3),
    )
    artifact_b = build_artifact(
        horizons=(1, 5),
    )

    with pytest.raises(
        ValueError,
        match="same comparison horizons",
    ):
        (
            CompareIndicatorComparativeResearchArtifacts()
            .execute(
                artifact_a,
                artifact_b,
            )
        )


def test_rejects_duplicate_horizon() -> None:
    artifact = build_artifact(
        horizons=(1, 1),
    )

    with pytest.raises(
        ValueError,
        match="duplicate comparison horizon 1",
    ):
        (
            CompareIndicatorComparativeResearchArtifacts()
            .execute(
                artifact,
                build_artifact(
                    horizons=(1,),
                ),
            )
        )


def test_rejects_non_array_comparisons() -> None:
    artifact = build_artifact()
    analysis = artifact["analysis"]

    assert isinstance(analysis, dict)

    analysis["comparisons"] = {}

    with pytest.raises(
        ValueError,
        match="comparisons must be an array",
    ):
        (
            CompareIndicatorComparativeResearchArtifacts()
            .execute(
                artifact,
                build_artifact(),
            )
        )


@pytest.mark.parametrize(
    "metric_value",
    [
        None,
        True,
        inf,
    ],
)
def test_rejects_invalid_metric(
    metric_value: object,
) -> None:
    artifact = build_artifact()
    analysis = artifact["analysis"]

    assert isinstance(analysis, dict)

    comparisons = analysis["comparisons"]

    assert isinstance(comparisons, list)
    assert isinstance(comparisons[0], dict)

    comparisons[0][
        "mean_return_difference"
    ] = metric_value

    with pytest.raises(
        ValueError,
        match=(
            "mean_return_difference "
            "must be"
        ),
    ):
        (
            CompareIndicatorComparativeResearchArtifacts()
            .execute(
                artifact,
                build_artifact(),
            )
        )


def test_rejects_missing_fingerprint() -> None:
    artifact = build_artifact()
    indicator = artifact["indicator"]

    assert isinstance(indicator, dict)

    del indicator["research_fingerprint"]

    with pytest.raises(
        ValueError,
        match=(
            "research_fingerprint must be "
            "a non-empty string"
        ),
    ):
        (
            CompareIndicatorComparativeResearchArtifacts()
            .execute(
                artifact,
                build_artifact(),
            )
        )


def test_rejects_non_dictionary_artifact() -> None:
    with pytest.raises(
        TypeError,
        match="artifact_a must be a dictionary",
    ):
        (
            CompareIndicatorComparativeResearchArtifacts()
            .execute(
                [],
                build_artifact(),
            )
        )
