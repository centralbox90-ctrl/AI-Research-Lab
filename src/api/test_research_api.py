from src.api import create_research_api


class StubGetStoredResearchArtifact:
    def __init__(
        self,
        artifacts: dict[
            str,
            dict[str, object],
        ],
    ) -> None:
        self.artifacts = artifacts
        self.calls: list[str] = []

    def execute(
        self,
        result_id: str,
    ) -> dict[str, object] | None:
        self.calls.append(result_id)

        return self.artifacts.get(result_id)


class StubListStoredResearchCycles:
    def __init__(
        self,
        result_ids: list[str],
    ) -> None:
        self.result_ids = result_ids
        self.calls = 0

    def execute(self) -> list[str]:
        self.calls += 1

        return list(self.result_ids)


class MissingExecute:
    pass


def test_lists_stored_research_cycles(
) -> None:
    use_case = StubListStoredResearchCycles(
        [
            "result-002",
            "result-001",
        ]
    )
    application = create_research_api(
        get_stored_research_artifact=(
            StubGetStoredResearchArtifact({})
        ),
        list_stored_research_cycles=use_case,
    )
    client = application.test_client()

    response = client.get(
        "/v1/research-cycles"
    )

    assert response.status_code == 200
    assert response.content_type == (
        "application/json"
    )
    assert response.get_json() == {
        "schema_version": 1,
        "count": 2,
        "result_ids": [
            "result-002",
            "result-001",
        ],
    }
    assert use_case.calls == 1


def test_lists_empty_research_cycle_collection(
) -> None:
    use_case = StubListStoredResearchCycles([])
    application = create_research_api(
        get_stored_research_artifact=(
            StubGetStoredResearchArtifact({})
        ),
        list_stored_research_cycles=use_case,
    )
    client = application.test_client()

    response = client.get(
        "/v1/research-cycles"
    )

    assert response.status_code == 200
    assert response.get_json() == {
        "schema_version": 1,
        "count": 0,
        "result_ids": [],
    }
    assert use_case.calls == 1


def test_rejects_invalid_application_dependency(
) -> None:
    try:
        create_research_api(
            get_stored_research_artifact=(
                StubGetStoredResearchArtifact({})
            ),
            list_stored_research_cycles=(
                MissingExecute()
            ),
        )
    except TypeError as error:
        assert str(error) == (
            "list_stored_research_cycles must "
            "provide a callable execute method"
        )
    else:
        raise AssertionError(
            "TypeError was not raised"
        )


def test_gets_stored_research_artifact(
) -> None:
    artifact_use_case = (
        StubGetStoredResearchArtifact(
            {
                "result-001": {
                    "artifact_type": (
                        "market_research"
                    ),
                    "schema_version": 1,
                },
            }
        )
    )
    application = create_research_api(
        get_stored_research_artifact=(
            artifact_use_case
        ),
        list_stored_research_cycles=(
            StubListStoredResearchCycles([])
        ),
    )
    client = application.test_client()

    response = client.get(
        "/v1/research-artifacts/result-001"
    )

    assert response.status_code == 200
    assert response.get_json() == {
        "schema_version": 1,
        "result_id": "result-001",
        "artifact": {
            "artifact_type": "market_research",
            "schema_version": 1,
        },
    }
    assert artifact_use_case.calls == [
        "result-001",
    ]


def test_reports_missing_research_artifact(
) -> None:
    artifact_use_case = (
        StubGetStoredResearchArtifact({})
    )
    application = create_research_api(
        get_stored_research_artifact=(
            artifact_use_case
        ),
        list_stored_research_cycles=(
            StubListStoredResearchCycles([])
        ),
    )
    client = application.test_client()

    response = client.get(
        "/v1/research-artifacts/unknown-result"
    )

    assert response.status_code == 404
    assert response.get_json() == {
        "schema_version": 1,
        "error": {
            "code": (
                "research_artifact_not_found"
            ),
            "message": (
                "Research artifact not found: "
                "unknown-result"
            ),
        },
    }
    assert artifact_use_case.calls == [
        "unknown-result",
    ]


def test_rejects_invalid_artifact_dependency(
) -> None:
    try:
        create_research_api(
            get_stored_research_artifact=(
                MissingExecute()
            ),
            list_stored_research_cycles=(
                StubListStoredResearchCycles([])
            ),
        )
    except TypeError as error:
        assert str(error) == (
            "get_stored_research_artifact must "
            "provide a callable execute method"
        )
    else:
        raise AssertionError(
            "TypeError was not raised"
        )