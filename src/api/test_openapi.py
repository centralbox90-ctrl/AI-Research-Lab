from src.api.openapi import (
    build_openapi_document,
)


def test_builds_openapi_31_document(
) -> None:
    document = build_openapi_document()

    assert document["openapi"] == "3.1.0"
    assert document["info"] == {
        "title": "AI Research Lab API",
        "version": "1.1.0",
        "description": (
            "Read-only access to stored "
            "research results."
        ),
    }

    paths = document["paths"]

    assert set(paths) == {
        "/v1/research-artifact-comparisons",
        "/v1/research-cycles",
        (
            "/v1/research-artifacts/"
            "{result_id}"
        ),
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


def test_defines_exact_transport_schemas(
) -> None:
    document = build_openapi_document()
    schemas = document[
        "components"
    ]["schemas"]

    assert set(schemas) == {
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