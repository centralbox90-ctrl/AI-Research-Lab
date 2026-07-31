from src.api import create_research_api
from src.application.artifact_comparison_factory import (
    ArtifactComparisonFactory,
)
from src.application.public_api import (
    StoredResearchArtifactIntegrityError,
)


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


class FailingGetStoredResearchArtifact:
    def execute(
        self,
        result_id: str,
    ):
        raise StoredResearchArtifactIntegrityError(
            result_id=result_id,
            reason="payload fingerprint mismatch",
        )


class FailingListStoredResearchCycles:
    def execute(self):
        raise StoredResearchArtifactIntegrityError(
            result_id="result-corrupt",
            reason="storage identity mismatch",
        )


class StubCompareStoredResearchArtifacts:
    def __init__(
        self,
        error: ValueError | None = None,
    ) -> None:
        self.error = error
        self.calls: list[tuple[str, str]] = []

    def execute(
        self,
        artifact_a_result_id: str,
        artifact_b_result_id: str,
    ):
        self.calls.append(
            (
                artifact_a_result_id,
                artifact_b_result_id,
            )
        )

        if self.error is not None:
            raise self.error

        return ArtifactComparisonFactory().create(
            artifact_a_id="artifact-001",
            artifact_b_id="artifact-002",
            previous_hypothesis="Previous hypothesis",
            current_hypothesis="Current hypothesis",
            hypothesis_change_reason=(
                "Hypothesis changed."
            ),
            previous_evidence={
                "net_profit": 1.0,
            },
            current_evidence={
                "net_profit": 2.5,
            },
            evidence_change_reason=(
                "Evidence changed."
            ),
            previous_confidence=0.4,
            current_confidence=0.7,
            confidence_change_reason=(
                "Confidence increased."
            ),
        )


class MissingExecute:
    pass


def test_requires_valid_bearer_token(
) -> None:
    list_use_case = StubListStoredResearchCycles(
        [
            "result-001",
        ]
    )
    application = create_research_api(
        compare_stored_research_artifacts=(
            StubCompareStoredResearchArtifacts()
        ),
        get_stored_research_artifact=(
            StubGetStoredResearchArtifact({})
        ),
        list_stored_research_cycles=(
            list_use_case
        ),
        api_token="private-api-token-value",
    )
    client = application.test_client()

    missing_response = client.get(
        "/v1/research-cycles"
    )

    assert missing_response.status_code == 401
    assert missing_response.get_json() == {
        "schema_version": 1,
        "error": {
            "code": "unauthorized",
            "message": (
                "A valid Bearer token is required."
            ),
        },
    }
    assert (
        missing_response.headers[
            "WWW-Authenticate"
        ]
        == 'Bearer realm="ai-research-lab"'
    )
    assert list_use_case.calls == 0

    invalid_response = client.get(
        "/v1/research-cycles",
        headers={
            "Authorization": "Bearer invalid-token",
        },
    )

    assert invalid_response.status_code == 401
    assert list_use_case.calls == 0

    authorized_response = client.get(
        "/v1/research-cycles",
        headers={
            "Authorization": (
                "Bearer private-api-token-value"
            ),
        },
    )

    assert authorized_response.status_code == 200
    assert list_use_case.calls == 1

    openapi_response = client.get(
        "/openapi.json",
        headers={
            "Authorization": (
                "Bearer private-api-token-value"
            ),
        },
    )

    assert openapi_response.status_code == 200
    assert openapi_response.get_json()[
        "security"
    ] == [
        {
            "BearerAuth": [],
        },
    ]


def test_rejects_invalid_api_token_configuration(
) -> None:
    invalid_configurations = (
        (
            "",
            "api_token must not be empty",
        ),
        (
            "   ",
            "api_token must not be empty",
        ),
        (
            " private-api-token ",
            (
                "api_token must not contain "
                "surrounding whitespace"
            ),
        ),
    )

    for api_token, expected_message in (
        invalid_configurations
    ):
        try:
            create_research_api(
                compare_stored_research_artifacts=(
                    StubCompareStoredResearchArtifacts()
                ),
                get_stored_research_artifact=(
                    StubGetStoredResearchArtifact({})
                ),
                list_stored_research_cycles=(
                    StubListStoredResearchCycles([])
                ),
                api_token=api_token,
            )
        except ValueError as error:
            assert str(error) == expected_message
        else:
            raise AssertionError(
                "ValueError was not raised"
            )


def test_lists_stored_research_cycles(
) -> None:
    use_case = StubListStoredResearchCycles(
        [
            "result-002",
            "result-001",
        ]
    )
    application = create_research_api(
        compare_stored_research_artifacts=(
            StubCompareStoredResearchArtifacts()
        ),
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
        compare_stored_research_artifacts=(
            StubCompareStoredResearchArtifacts()
        ),
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
            compare_stored_research_artifacts=(
                StubCompareStoredResearchArtifacts()
            ),
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
        compare_stored_research_artifacts=(
            StubCompareStoredResearchArtifacts()
        ),
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
        compare_stored_research_artifacts=(
            StubCompareStoredResearchArtifacts()
        ),
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
            compare_stored_research_artifacts=(
                StubCompareStoredResearchArtifacts()
            ),
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

def test_serves_openapi_document(
) -> None:
    application = create_research_api(
        compare_stored_research_artifacts=(
            StubCompareStoredResearchArtifacts()
        ),
        get_stored_research_artifact=(
            StubGetStoredResearchArtifact({})
        ),
        list_stored_research_cycles=(
            StubListStoredResearchCycles([])
        ),
    )
    client = application.test_client()

    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert response.content_type == (
        "application/json"
    )

    document = response.get_json()

    assert document["openapi"] == "3.1.0"
    assert document["info"]["version"] == (
        "1.2.0"
    )
    assert set(document["paths"]) == {
        "/v1/research-artifact-comparisons",
        "/v1/research-cycles",
        (
            "/v1/research-artifacts/"
            "{result_id}"
        ),
    }

def test_compares_stored_research_artifacts(
) -> None:
    use_case = StubCompareStoredResearchArtifacts()
    application = create_research_api(
        compare_stored_research_artifacts=use_case,
        get_stored_research_artifact=(
            StubGetStoredResearchArtifact({})
        ),
        list_stored_research_cycles=(
            StubListStoredResearchCycles([])
        ),
    )
    client = application.test_client()

    response = client.get(
        "/v1/research-artifact-comparisons",
        query_string={
            "artifact_a_result_id": "result-001",
            "artifact_b_result_id": "result-002",
        },
    )

    assert response.status_code == 200
    assert use_case.calls == [
        (
            "result-001",
            "result-002",
        ),
    ]

    payload = response.get_json()

    assert payload["schema_version"] == 1
    assert payload["artifact_a_result_id"] == (
        "result-001"
    )
    assert payload["artifact_b_result_id"] == (
        "result-002"
    )
    assert payload["comparison"]["artifact_a_id"] == (
        "artifact-001"
    )
    assert payload["comparison"]["artifact_b_id"] == (
        "artifact-002"
    )
    assert (
        payload["comparison"]
        ["confidence_evolution"]
        ["current_confidence"]
        == 0.7
    )
    assert (
        payload["comparison"]
        ["evidence_evolution"]
        ["metric_deltas"][0]
        ["absolute_delta"]
        == 1.5
    )


def test_rejects_incomplete_artifact_comparison_request(
) -> None:
    use_case = StubCompareStoredResearchArtifacts()
    application = create_research_api(
        compare_stored_research_artifacts=use_case,
        get_stored_research_artifact=(
            StubGetStoredResearchArtifact({})
        ),
        list_stored_research_cycles=(
            StubListStoredResearchCycles([])
        ),
    )
    client = application.test_client()

    response = client.get(
        "/v1/research-artifact-comparisons",
        query_string={
            "artifact_a_result_id": "result-001",
        },
    )

    assert response.status_code == 400
    assert response.get_json() == {
        "schema_version": 1,
        "error": {
            "code": (
                "invalid_artifact_comparison_request"
            ),
            "message": (
                "artifact_a_result_id and "
                "artifact_b_result_id are required"
            ),
        },
    }
    assert use_case.calls == []


def test_reports_missing_comparison_artifact(
) -> None:
    use_case = StubCompareStoredResearchArtifacts(
        ValueError(
            "Research artifact was not found "
            "for result_id: result-404"
        )
    )
    application = create_research_api(
        compare_stored_research_artifacts=use_case,
        get_stored_research_artifact=(
            StubGetStoredResearchArtifact({})
        ),
        list_stored_research_cycles=(
            StubListStoredResearchCycles([])
        ),
    )
    client = application.test_client()

    response = client.get(
        "/v1/research-artifact-comparisons",
        query_string={
            "artifact_a_result_id": "result-001",
            "artifact_b_result_id": "result-404",
        },
    )

    assert response.status_code == 404
    assert response.get_json() == {
        "schema_version": 1,
        "error": {
            "code": "research_artifact_not_found",
            "message": (
                "Research artifact was not found "
                "for result_id: result-404"
            ),
        },
    }


def test_rejects_invalid_comparison_dependency(
) -> None:
    try:
        create_research_api(
            compare_stored_research_artifacts=(
                MissingExecute()
            ),
            get_stored_research_artifact=(
                StubGetStoredResearchArtifact({})
            ),
            list_stored_research_cycles=(
                StubListStoredResearchCycles([])
            ),
        )
    except TypeError as error:
        assert str(error) == (
            "compare_stored_research_artifacts must "
            "provide a callable execute method"
        )
    else:
        raise AssertionError(
            "TypeError was not raised"
        )


def test_reports_stored_artifact_integrity_error(
) -> None:
    application = create_research_api(
        compare_stored_research_artifacts=(
            StubCompareStoredResearchArtifacts()
        ),
        get_stored_research_artifact=(
            FailingGetStoredResearchArtifact()
        ),
        list_stored_research_cycles=(
            StubListStoredResearchCycles([])
        ),
    )
    response = application.test_client().get(
        "/v1/research-artifacts/result-corrupt"
    )

    assert response.status_code == 422
    assert response.get_json() == {
        "schema_version": 1,
        "error": {
            "code": (
                "stored_research_artifact_"
                "integrity_error"
            ),
            "message": (
                "stored research artifact "
                "'result-corrupt' failed integrity "
                "validation: payload fingerprint mismatch"
            ),
            "result_id": "result-corrupt",
            "reason": "payload fingerprint mismatch",
        },
    }


def test_reports_stored_artifact_listing_integrity_error(
) -> None:
    application = create_research_api(
        compare_stored_research_artifacts=(
            StubCompareStoredResearchArtifacts()
        ),
        get_stored_research_artifact=(
            StubGetStoredResearchArtifact({})
        ),
        list_stored_research_cycles=(
            FailingListStoredResearchCycles()
        ),
    )
    response = application.test_client().get(
        "/v1/research-cycles"
    )

    assert response.status_code == 422
    assert response.get_json() == {
        "schema_version": 1,
        "error": {
            "code": (
                "stored_research_artifact_"
                "integrity_error"
            ),
            "message": (
                "stored research artifact "
                "'result-corrupt' failed integrity "
                "validation: storage identity mismatch"
            ),
            "result_id": "result-corrupt",
            "reason": "storage identity mismatch",
        },
    }
