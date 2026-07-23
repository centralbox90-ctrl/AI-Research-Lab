import json
from pathlib import Path

import pytest

from src.application.indicator_comparative_research_artifact_loader import (
    IndicatorComparativeResearchArtifactLoader,
)


def build_payload() -> dict[str, object]:
    return {
        "artifact_type": (
            "indicator_comparative_research"
        ),
        "artifact_version": 1,
        "indicator": {
            "id": "rsi",
        },
        "market": {
            "symbol": "EURUSD",
            "timeframe": "H1",
        },
        "dataset": {
            "id": "dataset-id",
        },
        "outcome_specification": {
            "horizons": [1, 3, 5],
            "price_field": "close",
        },
        "analysis": {
            "comparisons": [],
        },
    }


def test_loads_valid_artifact(
    tmp_path: Path,
) -> None:
    artifact_path = (
        tmp_path
        / "comparative-result.json"
    )
    payload = build_payload()
    artifact_path.write_text(
        json.dumps(payload),
        encoding="utf-8",
    )

    loaded = (
        IndicatorComparativeResearchArtifactLoader()
        .load(artifact_path)
    )

    assert loaded == payload


def test_from_dict_returns_copy() -> None:
    payload = build_payload()

    loaded = (
        IndicatorComparativeResearchArtifactLoader()
        .from_dict(payload)
    )

    assert loaded == payload
    assert loaded is not payload


def test_rejects_unreadable_file(
    tmp_path: Path,
) -> None:
    artifact_path = tmp_path / "missing.json"

    with pytest.raises(
        ValueError,
        match=(
            "unable to read comparative "
            "research artifact"
        ),
    ):
        (
            IndicatorComparativeResearchArtifactLoader()
            .load(artifact_path)
        )


def test_rejects_invalid_json(
    tmp_path: Path,
) -> None:
    artifact_path = tmp_path / "invalid.json"
    artifact_path.write_text(
        "{",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match=(
            "invalid comparative research "
            "artifact JSON"
        ),
    ):
        (
            IndicatorComparativeResearchArtifactLoader()
            .load(artifact_path)
        )


@pytest.mark.parametrize(
    "payload",
    [
        [],
        "artifact",
        None,
    ],
)
def test_rejects_non_object_payload(
    payload: object,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "comparative research artifact JSON "
            "must contain an object"
        ),
    ):
        (
            IndicatorComparativeResearchArtifactLoader()
            .from_dict(payload)
        )


@pytest.mark.parametrize(
    "artifact_type",
    [
        None,
        "research_artifact",
        1,
    ],
)
def test_rejects_invalid_artifact_type(
    artifact_type: object,
) -> None:
    payload = build_payload()
    payload["artifact_type"] = artifact_type

    with pytest.raises(
        ValueError,
        match="artifact_type must be",
    ):
        (
            IndicatorComparativeResearchArtifactLoader()
            .from_dict(payload)
        )


@pytest.mark.parametrize(
    "artifact_version",
    [
        None,
        2,
        "1",
        True,
    ],
)
def test_rejects_invalid_artifact_version(
    artifact_version: object,
) -> None:
    payload = build_payload()
    payload["artifact_version"] = (
        artifact_version
    )

    with pytest.raises(
        ValueError,
        match="artifact_version must be 1",
    ):
        (
            IndicatorComparativeResearchArtifactLoader()
            .from_dict(payload)
        )


def test_rejects_missing_required_section(
) -> None:
    payload = build_payload()
    del payload["analysis"]

    with pytest.raises(
        ValueError,
        match=(
            "missing comparative research "
            "artifact sections: analysis"
        ),
    ):
        (
            IndicatorComparativeResearchArtifactLoader()
            .from_dict(payload)
        )


def test_rejects_non_object_section(
) -> None:
    payload = build_payload()
    payload["analysis"] = []

    with pytest.raises(
        ValueError,
        match="analysis must be an object",
    ):
        (
            IndicatorComparativeResearchArtifactLoader()
            .from_dict(payload)
        )
