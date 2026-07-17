from typing import Any

from app.web import (
    create_app,
    sort_artifacts,
)


class FakeStoredResearchCycleLister:
    def execute(self) -> list[str]:
        return [
            "result-old",
            "result-new",
            "result-middle",
        ]


class FakeStoredResearchArtifactGetter:
    def __init__(
        self,
        artifacts: dict[str, dict[str, Any]],
    ) -> None:
        self.artifacts = artifacts

    def execute(
        self,
        result_id: str,
    ) -> dict[str, Any] | None:
        return self.artifacts.get(result_id)


def build_summary(
    *,
    result_id: str,
    symbol: str,
    confidence: float | None,
    created_at: str,
    depth: int,
) -> dict[str, Any]:
    return {
        "result_id": result_id,
        "artifact_id": f"artifact-{result_id}",
        "parent_artifact_id": None,
        "parent_result_id": None,
        "lineage_type": "root",
        "depth": depth,
        "symbol": symbol,
        "timeframe": "1h",
        "hypothesis": f"Hypothesis {result_id}",
        "confidence": confidence,
        "created_at": created_at,
    }


def build_artifact(
    *,
    artifact_id: str,
    symbol: str,
    confidence: float,
    created_at: str,
    parent_artifact_id: str | None = None,
) -> dict[str, Any]:
    return {
        "artifact_version": 1,
        "metadata": {
            "artifact_id": artifact_id,
            "created_at": created_at,
            "executor_type": "market_backtest",
            "data_source": "historical",
        },
        "specification": {
            "hypothesis_description": (
                f"Hypothesis for {symbol}"
            ),
            "symbol": symbol,
            "timeframe": "1h",
        },
        "cycle": {
            "evidence_strength_evaluation": {
                "score": confidence,
            },
        },
        "lineage": {
            "parent_artifact_id": parent_artifact_id,
            "lineage_type": (
                "root"
                if parent_artifact_id is None
                else "hypothesis_refinement"
            ),
        },
    }


def build_artifacts() -> dict[str, dict[str, Any]]:
    return {
        "result-old": build_artifact(
            artifact_id="artifact-old",
            symbol="BTCUSDT",
            confidence=0.31,
            created_at="2026-07-10T10:00:00+00:00",
        ),
        "result-new": build_artifact(
            artifact_id="artifact-new",
            symbol="ETHUSDT",
            confidence=0.82,
            created_at="2026-07-20T10:00:00+00:00",
            parent_artifact_id="artifact-middle",
        ),
        "result-middle": build_artifact(
            artifact_id="artifact-middle",
            symbol="ADAUSDT",
            confidence=0.55,
            created_at="2026-07-15T10:00:00+00:00",
            parent_artifact_id="artifact-old",
        ),
    }


def extract_artifact_positions(
    body: str,
) -> dict[str, int]:
    section_start = body.rfind(
        "<h2>Research artifacts</h2>"
    )

    assert section_start != -1

    artifacts_section = body[
        section_start:
    ]

    return {
        "result-old": artifacts_section.find(
            "<dd>result-old</dd>"
        ),
        "result-new": artifacts_section.find(
            "<dd>result-new</dd>"
        ),
        "result-middle": artifacts_section.find(
            "<dd>result-middle</dd>"
        ),
    }

def test_sort_artifacts_by_created_at_descending():

    artifacts = [
        build_summary(
            result_id="result-old",
            symbol="BTCUSDT",
            confidence=0.31,
            created_at="2026-07-10T10:00:00+00:00",
            depth=0,
        ),
        build_summary(
            result_id="result-new",
            symbol="ETHUSDT",
            confidence=0.82,
            created_at="2026-07-20T10:00:00+00:00",
            depth=2,
        ),
        build_summary(
            result_id="result-middle",
            symbol="ADAUSDT",
            confidence=0.55,
            created_at="2026-07-15T10:00:00+00:00",
            depth=1,
        ),
    ]

    sorted_artifacts = sort_artifacts(
        artifacts=artifacts,
        sort_by="created_at",
        descending=True,
    )

    assert [
        artifact["result_id"]
        for artifact in sorted_artifacts
    ] == [
        "result-new",
        "result-middle",
        "result-old",
    ]


def test_sort_artifacts_by_created_at_ascending():

    artifacts = [
        build_summary(
            result_id="result-old",
            symbol="BTCUSDT",
            confidence=0.31,
            created_at="2026-07-10T10:00:00+00:00",
            depth=0,
        ),
        build_summary(
            result_id="result-new",
            symbol="ETHUSDT",
            confidence=0.82,
            created_at="2026-07-20T10:00:00+00:00",
            depth=2,
        ),
        build_summary(
            result_id="result-middle",
            symbol="ADAUSDT",
            confidence=0.55,
            created_at="2026-07-15T10:00:00+00:00",
            depth=1,
        ),
    ]

    sorted_artifacts = sort_artifacts(
        artifacts=artifacts,
        sort_by="created_at",
        descending=False,
    )

    assert [
        artifact["result_id"]
        for artifact in sorted_artifacts
    ] == [
        "result-old",
        "result-middle",
        "result-new",
    ]


def test_sort_artifacts_by_confidence_descending():

    artifacts = [
        build_summary(
            result_id="result-old",
            symbol="BTCUSDT",
            confidence=0.31,
            created_at="2026-07-10T10:00:00+00:00",
            depth=0,
        ),
        build_summary(
            result_id="result-new",
            symbol="ETHUSDT",
            confidence=0.82,
            created_at="2026-07-20T10:00:00+00:00",
            depth=2,
        ),
        build_summary(
            result_id="result-middle",
            symbol="ADAUSDT",
            confidence=0.55,
            created_at="2026-07-15T10:00:00+00:00",
            depth=1,
        ),
    ]

    sorted_artifacts = sort_artifacts(
        artifacts=artifacts,
        sort_by="confidence",
        descending=True,
    )

    assert [
        artifact["result_id"]
        for artifact in sorted_artifacts
    ] == [
        "result-new",
        "result-middle",
        "result-old",
    ]


def test_sort_artifacts_by_symbol_ascending():

    artifacts = [
        build_summary(
            result_id="result-old",
            symbol="BTCUSDT",
            confidence=0.31,
            created_at="2026-07-10T10:00:00+00:00",
            depth=0,
        ),
        build_summary(
            result_id="result-new",
            symbol="ETHUSDT",
            confidence=0.82,
            created_at="2026-07-20T10:00:00+00:00",
            depth=2,
        ),
        build_summary(
            result_id="result-middle",
            symbol="ADAUSDT",
            confidence=0.55,
            created_at="2026-07-15T10:00:00+00:00",
            depth=1,
        ),
    ]

    sorted_artifacts = sort_artifacts(
        artifacts=artifacts,
        sort_by="symbol",
        descending=False,
    )

    assert [
        artifact["symbol"]
        for artifact in sorted_artifacts
    ] == [
        "ADAUSDT",
        "BTCUSDT",
        "ETHUSDT",
    ]


def test_sort_artifacts_by_lineage_depth_descending():

    artifacts = [
        build_summary(
            result_id="result-old",
            symbol="BTCUSDT",
            confidence=0.31,
            created_at="2026-07-10T10:00:00+00:00",
            depth=0,
        ),
        build_summary(
            result_id="result-new",
            symbol="ETHUSDT",
            confidence=0.82,
            created_at="2026-07-20T10:00:00+00:00",
            depth=2,
        ),
        build_summary(
            result_id="result-middle",
            symbol="ADAUSDT",
            confidence=0.55,
            created_at="2026-07-15T10:00:00+00:00",
            depth=1,
        ),
    ]

    sorted_artifacts = sort_artifacts(
        artifacts=artifacts,
        sort_by="lineage_depth",
        descending=True,
    )

    assert [
        artifact["depth"]
        for artifact in sorted_artifacts
    ] == [
        2,
        1,
        0,
    ]


def test_sort_artifacts_handles_missing_confidence():

    artifacts = [
        build_summary(
            result_id="result-known",
            symbol="BTCUSDT",
            confidence=0.5,
            created_at="2026-07-10T10:00:00+00:00",
            depth=0,
        ),
        build_summary(
            result_id="result-missing",
            symbol="ETHUSDT",
            confidence=None,
            created_at="2026-07-20T10:00:00+00:00",
            depth=0,
        ),
    ]

    sorted_artifacts = sort_artifacts(
        artifacts=artifacts,
        sort_by="confidence",
        descending=True,
    )

    assert [
        artifact["result_id"]
        for artifact in sorted_artifacts
    ] == [
        "result-known",
        "result-missing",
    ]


def test_web_index_sorts_by_created_at_descending():

    app = create_app(
        cycle_lister=FakeStoredResearchCycleLister(),
        artifact_getter=FakeStoredResearchArtifactGetter(
            artifacts=build_artifacts(),
        ),
    )

    client = app.test_client()

    response = client.get(
        "/?sort_by=created_at"
        "&sort_direction=descending"
    )

    assert response.status_code == 200

    body = response.get_data(
        as_text=True,
    )

    positions = extract_artifact_positions(body)

    assert (
        positions["result-new"]
        < positions["result-middle"]
        < positions["result-old"]
    )


def test_web_index_sorts_by_confidence_ascending():

    app = create_app(
        cycle_lister=FakeStoredResearchCycleLister(),
        artifact_getter=FakeStoredResearchArtifactGetter(
            artifacts=build_artifacts(),
        ),
    )

    client = app.test_client()

    response = client.get(
        "/?sort_by=confidence"
        "&sort_direction=ascending"
    )

    assert response.status_code == 200

    body = response.get_data(
        as_text=True,
    )

    positions = extract_artifact_positions(body)

    assert (
        positions["result-old"]
        < positions["result-middle"]
        < positions["result-new"]
    )


def test_web_index_sorts_by_symbol_ascending():

    app = create_app(
        cycle_lister=FakeStoredResearchCycleLister(),
        artifact_getter=FakeStoredResearchArtifactGetter(
            artifacts=build_artifacts(),
        ),
    )

    client = app.test_client()

    response = client.get(
        "/?sort_by=symbol"
        "&sort_direction=ascending"
    )

    assert response.status_code == 200

    body = response.get_data(
        as_text=True,
    )

    positions = extract_artifact_positions(body)

    assert (
        positions["result-middle"]
        < positions["result-old"]
        < positions["result-new"]
    )


def test_web_index_sorts_by_lineage_depth_descending():

    app = create_app(
        cycle_lister=FakeStoredResearchCycleLister(),
        artifact_getter=FakeStoredResearchArtifactGetter(
            artifacts=build_artifacts(),
        ),
    )

    client = app.test_client()

    response = client.get(
        "/?sort_by=lineage_depth"
        "&sort_direction=descending"
    )

    assert response.status_code == 200

    body = response.get_data(
        as_text=True,
    )

    positions = extract_artifact_positions(body)

    assert (
        positions["result-new"]
        < positions["result-middle"]
        < positions["result-old"]
    )

    assert "<dd>2</dd>" in body
    assert "<dd>1</dd>" in body
    assert "<dd>0</dd>" in body


def test_web_index_falls_back_for_invalid_sorting():

    app = create_app(
        cycle_lister=FakeStoredResearchCycleLister(),
        artifact_getter=FakeStoredResearchArtifactGetter(
            artifacts=build_artifacts(),
        ),
    )

    client = app.test_client()

    response = client.get(
        "/?sort_by=invalid"
        "&sort_direction=invalid"
    )

    assert response.status_code == 200

    body = response.get_data(
        as_text=True,
    )

    positions = extract_artifact_positions(body)

    assert (
        positions["result-new"]
        < positions["result-middle"]
        < positions["result-old"]
    )

    assert 'value="created_at"' in body
    assert 'value="descending"' in body


def test_web_index_combines_filtering_and_sorting():

    app = create_app(
        cycle_lister=FakeStoredResearchCycleLister(),
        artifact_getter=FakeStoredResearchArtifactGetter(
            artifacts=build_artifacts(),
        ),
    )

    client = app.test_client()

    response = client.get(
        "/?timeframe=1h"
        "&sort_by=confidence"
        "&sort_direction=descending"
    )

    assert response.status_code == 200

    body = response.get_data(
        as_text=True,
    )

    assert "Showing 3 of 3 research artifacts." in body

    positions = extract_artifact_positions(body)

    assert (
        positions["result-new"]
        < positions["result-middle"]
        < positions["result-old"]
    )