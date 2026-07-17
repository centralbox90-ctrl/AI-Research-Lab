from typing import Any

import pytest

from src.application.compare_stored_research_artifacts import (
    CompareStoredResearchArtifacts,
)


class FakeArtifactGetter:
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


class FakeComparisonInputExtractor:
    def extract(
        self,
        artifact_a: dict[str, Any],
        artifact_b: dict[str, Any],
    ) -> dict[str, Any]:
        raise AssertionError(
            "Extractor must not be called when an artifact is missing."
        )


def test_compare_stored_research_artifacts_raises_when_first_artifact_missing():

    use_case = CompareStoredResearchArtifacts(
        artifact_getter=FakeArtifactGetter(
            artifacts={}
        ),
        input_extractor=FakeComparisonInputExtractor(),
    )

    with pytest.raises(
        ValueError,
        match=(
            "Research artifact was not found for result_id: "
            "result-001"
        ),
    ):
        use_case.execute(
            artifact_a_result_id="result-001",
            artifact_b_result_id="result-002",
        )


def test_compare_stored_research_artifacts_raises_when_second_artifact_missing():

    use_case = CompareStoredResearchArtifacts(
        artifact_getter=FakeArtifactGetter(
            artifacts={
                "result-001": {
                    "metadata": {
                        "artifact_id": "artifact-001",
                    }
                }
            }
        ),
        input_extractor=FakeComparisonInputExtractor(),
    )

    with pytest.raises(
        ValueError,
        match=(
            "Research artifact was not found for result_id: "
            "result-002"
        ),
    ):
        use_case.execute(
            artifact_a_result_id="result-001",
            artifact_b_result_id="result-002",
        )