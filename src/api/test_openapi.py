from src.api.openapi import (
    build_openapi_document,
)


def test_builds_openapi_31_document(
) -> None:
    document = build_openapi_document()

    assert document["openapi"] == "3.1.0"
    assert document["info"] == {
        "title": "AI Research Lab API",
        "version": "1.3.0",
        "description": (
            "Read-only access to stored "
            "research results."
        ),
    }

    paths = document["paths"]

    assert set(paths) == {
        "/health",
        "/ready",
        "/v1/research-artifact-comparisons",
        "/v1/research-cycles",
        (
            "/v1/research-artifacts/"
            "{result_id}"
        ),
    }

    health_operation = paths["/health"]["get"]
    readiness_operation = paths["/ready"]["get"]

    assert health_operation["operationId"] == (
        "getHealth"
    )
    assert health_operation["security"] == []
    assert set(health_operation["responses"]) == {
        "200",
    }
    assert readiness_operation["operationId"] == (
        "getReadiness"
    )
    assert readiness_operation["security"] == []
    assert set(
        readiness_operation["responses"]
    ) == {
        "200",
        "503",
    }

    assert paths[
        "/v1/research-cycles"
    ]["get"]["operationId"] == (
        "listResearchCycles"
    )

    artifact_operation = paths[
        (
            "/v1/research-artifacts/"
            "{result_id}"
        )
    ]["get"]

    assert artifact_operation[
        "operationId"
    ] == "getResearchArtifact"
    assert artifact_operation[
        "parameters"
    ] == [
        {
            "name": "result_id",
            "in": "path",
            "required": True,
            "description": (
                "Exact stored result "
                "identifier."
            ),
            "schema": {
                "type": "string",
                "minLength": 1,
            },
        },
    ]
    assert set(
        artifact_operation["responses"]
    ) == {
        "200",
        "404",
    }
    comparison_operation = paths[
        "/v1/research-artifact-comparisons"
    ]["get"]

    assert comparison_operation[
        "operationId"
    ] == "compareResearchArtifacts"
    assert [
        parameter["name"]
        for parameter in comparison_operation[
            "parameters"
        ]
    ] == [
        "artifact_a_result_id",
        "artifact_b_result_id",
    ]
    assert all(
        parameter["in"] == "query"
        and parameter["required"] is True
        for parameter in comparison_operation[
            "parameters"
        ]
    )
    assert set(
        comparison_operation["responses"]
    ) == {
        "200",
        "400",
        "404",
        "422",
    }


def test_documents_optional_bearer_authentication(
) -> None:
    local_document = build_openapi_document()

    assert "security" not in local_document
    assert (
        "securitySchemes"
        not in local_document["components"]
    )

    private_document = build_openapi_document(
        bearer_auth_required=True,
    )

    assert private_document["security"] == [
        {
            "BearerAuth": [],
        },
    ]
    assert private_document["components"][
        "securitySchemes"
    ] == {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
        },
    }

    unauthorized_schema = (
        private_document["components"]["schemas"][
            "UnauthorizedError"
        ]
    )

    assert unauthorized_schema["properties"][
        "error"
    ]["properties"]["code"]["const"] == (
        "unauthorized"
    )

    for path, path_item in private_document[
        "paths"
    ].items():
        for operation in path_item.values():
            if path in {
                "/health",
                "/ready",
            }:
                assert operation["security"] == []
                assert "401" not in operation["responses"]
                continue

            assert operation["responses"]["401"] == {
                "description": (
                    "A valid Bearer token "
                    "is required."
                ),
                "content": {
                    "application/json": {
                        "schema": {
                            "$ref": (
                                "#/components/"
                                "schemas/"
                                "UnauthorizedError"
                            ),
                        },
                    },
                },
            }


def test_defines_exact_transport_schemas(
) -> None:
    document = build_openapi_document()
    schemas = document[
        "components"
    ]["schemas"]

    assert set(schemas) == {
        "HealthStatus",
        "ReadinessStatus",
        "ServiceUnavailableError",
        "ResearchCycleList",
        "ResearchArtifact",
        "ResearchArtifactComparison",
        "ArtifactComparison",
        "HypothesisEvolution",
        "EvidenceEvolution",
        "EvidenceMetricDelta",
        "ConfidenceEvolution",
        "InvalidArtifactComparisonRequestError",
        "InvalidResearchArtifactComparisonError",
        "ApiError",
    }

    for schema in schemas.values():
        assert schema[
            "additionalProperties"
        ] is False

    assert schemas[
        "HealthStatus"
    ]["properties"]["status"]["const"] == (
        "healthy"
    )
    assert schemas[
        "ReadinessStatus"
    ]["properties"]["status"]["const"] == (
        "ready"
    )
    assert schemas[
        "ServiceUnavailableError"
    ]["properties"]["error"]["properties"][
        "code"
    ]["const"] == "service_unavailable"

    assert schemas[
        "ResearchArtifactComparison"
    ]["required"] == [
        "schema_version",
        "artifact_a_result_id",
        "artifact_b_result_id",
        "comparison",
    ]
    assert schemas[
        "EvidenceMetricDelta"
    ]["properties"]["direction"]["enum"] == [
        "increased",
        "decreased",
        "unchanged",
        "added",
        "removed",
        "not_comparable",
    ]
    assert schemas[
        "InvalidArtifactComparisonRequestError"
    ]["properties"]["error"]["properties"][
        "code"
    ]["const"] == (
        "invalid_artifact_comparison_request"
    )
    assert schemas[
        "InvalidResearchArtifactComparisonError"
    ]["properties"]["error"]["properties"][
        "code"
    ]["const"] == (
        "research_artifact_comparison_invalid"
    )
    assert schemas[
        "ResearchCycleList"
    ]["required"] == [
        "schema_version",
        "count",
        "result_ids",
    ]
    assert schemas[
        "ResearchArtifact"
    ]["properties"]["artifact"] == {
        "type": "object",
        "additionalProperties": True,
    }
    assert schemas[
        "ApiError"
    ]["properties"]["error"][
        "properties"
    ]["code"]["const"] == (
        "research_artifact_not_found"
    )