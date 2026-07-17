from typing import Any

from app.web import create_app


class FakeStoredResearchCycleLister:
    def execute(self) -> list[str]:
        return [
            "result-001",
            "result-002",
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


def build_artifact(
    *,
    artifact_id: str,
    symbol: str,
    parent_artifact_id: str | None = None,
) -> dict[str, Any]:
    return {
        "artifact_version": 1,
        "metadata": {
            "artifact_id": artifact_id,
            "created_at": "2026-07-16T10:00:00+00:00",
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
                "score": 0.5,
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
        "result-001": build_artifact(
            artifact_id="artifact-001",
            symbol="BTCUSDT",
        ),
        "result-002": build_artifact(
            artifact_id="artifact-002",
            symbol="ETHUSDT",
            parent_artifact_id="artifact-001",
        ),
    }


def build_app():
    return create_app(
        cycle_lister=FakeStoredResearchCycleLister(),
        artifact_getter=FakeStoredResearchArtifactGetter(
            artifacts=build_artifacts(),
        ),
    )


def test_web_index_renders_quick_navigation():

    response = build_app().test_client().get("/")

    assert response.status_code == 200

    body = response.get_data(
        as_text=True,
    )

    assert 'aria-label="Quick navigation"' in body

    assert 'href="#dashboard"' in body
    assert 'href="#filters"' in body
    assert 'href="#comparison"' in body
    assert 'href="#artifacts"' in body

    assert "Dashboard" in body
    assert "Filters" in body
    assert "Comparison" in body
    assert "Artifacts" in body


def test_web_index_renders_navigation_targets():

    response = build_app().test_client().get("/")

    assert response.status_code == 200

    body = response.get_data(
        as_text=True,
    )

    assert 'section id="dashboard"' in body
    assert 'section id="filters"' in body
    assert 'section id="comparison"' in body
    assert 'section id="artifacts"' in body


def test_web_index_navigation_targets_are_unique():

    response = build_app().test_client().get("/")

    assert response.status_code == 200

    body = response.get_data(
        as_text=True,
    )

    assert body.count('id="dashboard"') == 1
    assert body.count('id="filters"') == 1
    assert body.count('id="comparison"') == 1
    assert body.count('id="artifacts"') == 1


def test_web_index_keeps_navigation_with_empty_storage():

    app = create_app()

    response = app.test_client().get("/")

    assert response.status_code == 200

    body = response.get_data(
        as_text=True,
    )

    assert 'aria-label="Quick navigation"' in body
    assert 'href="#dashboard"' in body
    assert 'href="#filters"' in body
    assert 'href="#comparison"' in body
    assert 'href="#artifacts"' in body

    assert 'section id="dashboard"' in body
    assert 'section id="filters"' in body
    assert 'section id="comparison"' in body
    assert 'section id="artifacts"' in body