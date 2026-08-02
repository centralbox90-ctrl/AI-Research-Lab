from __future__ import annotations


def build_openapi_document(
    *,
    bearer_auth_required: bool = False,
) -> dict[str, object]:
    """
    Build the versioned HTTP transport contract.

    The document describes transport DTOs only.
    Domain and persistence models are not exposed.
    """

    if not isinstance(
        bearer_auth_required,
        bool,
    ):
        raise TypeError(
            "bearer_auth_required must be a boolean"
        )

    document = {
        "openapi": "3.1.0",
        "info": {
            "title": "AI Research Lab API",
            "version": "1.3.0",
            "description": (
                "Read-only access to stored "
                "research results."
            ),
        },
        "paths": {
            "/health": {
                "get": {
                    "operationId": "getHealth",
                    "summary": "Report process liveness",
                    "security": [],
                    "responses": {
                        "200": {
                            "description": (
                                "The HTTP process is alive."
                            ),
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": (
                                            "#/components/"
                                            "schemas/"
                                            "HealthStatus"
                                        ),
                                    },
                                },
                            },
                        },
                    },
                },
            },
            "/ready": {
                "get": {
                    "operationId": "getReadiness",
                    "summary": (
                        "Report service readiness"
                    ),
                    "security": [],
                    "responses": {
                        "200": {
                            "description": (
                                "The service and SQLite "
                                "storage are ready."
                            ),
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": (
                                            "#/components/"
                                            "schemas/"
                                            "ReadinessStatus"
                                        ),
                                    },
                                },
                            },
                        },
                        "503": {
                            "description": (
                                "The service is not ready."
                            ),
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": (
                                            "#/components/"
                                            "schemas/"
                                            "ServiceUnavailableError"
                                        ),
                                    },
                                },
                            },
                        },
                    },
                },
            },
            "/v1/research-artifact-comparisons": {
                "get": {
                    "operationId": (
                        "compareResearchArtifacts"
                    ),
                    "summary": (
                        "Compare two stored research "
                        "artifacts"
                    ),
                    "parameters": [
                        {
                            "name": (
                                "artifact_a_result_id"
                            ),
                            "in": "query",
                            "required": True,
                            "description": (
                                "Stored result identifier "
                                "for the previous artifact."
                            ),
                            "schema": {
                                "type": "string",
                                "minLength": 1,
                            },
                        },
                        {
                            "name": (
                                "artifact_b_result_id"
                            ),
                            "in": "query",
                            "required": True,
                            "description": (
                                "Stored result identifier "
                                "for the current artifact."
                            ),
                            "schema": {
                                "type": "string",
                                "minLength": 1,
                            },
                        },
                    ],
                    "responses": {
                        "200": {
                            "description": (
                                "Research artifact "
                                "comparison."
                            ),
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": (
                                            "#/components/"
                                            "schemas/"
                                            "ResearchArtifactComparison"
                                        ),
                                    },
                                },
                            },
                        },
                        "400": {
                            "description": (
                                "Required comparison "
                                "identifier is missing."
                            ),
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": (
                                            "#/components/"
                                            "schemas/"
                                            "InvalidArtifactComparison"
                                            "RequestError"
                                        ),
                                    },
                                },
                            },
                        },
                        "404": {
                            "description": (
                                "A research artifact "
                                "was not found."
                            ),
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": (
                                            "#/components/"
                                            "schemas/"
                                            "ApiError"
                                        ),
                                    },
                                },
                            },
                        },
                        "422": {
                            "description": (
                                "Stored artifacts cannot "
                                "be compared."
                            ),
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": (
                                            "#/components/"
                                            "schemas/"
                                            "InvalidResearchArtifact"
                                            "ComparisonError"
                                        ),
                                    },
                                },
                            },
                        },
                    },
                },
            },            "/v1/research-cycles": {
                "get": {
                    "operationId": (
                        "listResearchCycles"
                    ),
                    "summary": (
                        "List stored research "
                        "cycle identifiers"
                    ),
                    "responses": {
                        "200": {
                            "description": (
                                "Stored research "
                                "cycle identifiers."
                            ),
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": (
                                            "#/components/"
                                            "schemas/"
                                            "ResearchCycleList"
                                        ),
                                    },
                                },
                            },
                        },
                    },
                },
            },
            (
                "/v1/research-artifacts/"
                "{result_id}"
            ): {
                "get": {
                    "operationId": (
                        "getResearchArtifact"
                    ),
                    "summary": (
                        "Get a stored research "
                        "artifact"
                    ),
                    "parameters": [
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
                    ],
                    "responses": {
                        "200": {
                            "description": (
                                "Stored research "
                                "artifact."
                            ),
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": (
                                            "#/components/"
                                            "schemas/"
                                            "ResearchArtifact"
                                        ),
                                    },
                                },
                            },
                        },
                        "404": {
                            "description": (
                                "Research artifact "
                                "was not found."
                            ),
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": (
                                            "#/components/"
                                            "schemas/"
                                            "ApiError"
                                        ),
                                    },
                                },
                            },
                        },
                    },
                },
            },
        },
        "components": {
            "schemas": {
                "HealthStatus": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "schema_version",
                        "status",
                    ],
                    "properties": {
                        "schema_version": {
                            "type": "integer",
                            "const": 1,
                        },
                        "status": {
                            "type": "string",
                            "const": "healthy",
                        },
                    },
                },
                "ReadinessStatus": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "schema_version",
                        "status",
                    ],
                    "properties": {
                        "schema_version": {
                            "type": "integer",
                            "const": 1,
                        },
                        "status": {
                            "type": "string",
                            "const": "ready",
                        },
                    },
                },
                "ServiceUnavailableError": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "schema_version",
                        "error",
                    ],
                    "properties": {
                        "schema_version": {
                            "type": "integer",
                            "const": 1,
                        },
                        "error": {
                            "type": "object",
                            "additionalProperties": False,
                            "required": [
                                "code",
                                "message",
                            ],
                            "properties": {
                                "code": {
                                    "type": "string",
                                    "const": (
                                        "service_unavailable"
                                    ),
                                },
                                "message": {
                                    "type": "string",
                                    "minLength": 1,
                                },
                            },
                        },
                    },
                },
                "ResearchCycleList": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "schema_version",
                        "count",
                        "result_ids",
                    ],
                    "properties": {
                        "schema_version": {
                            "type": "integer",
                            "const": 1,
                        },
                        "count": {
                            "type": "integer",
                            "minimum": 0,
                        },
                        "result_ids": {
                            "type": "array",
                            "items": {
                                "type": "string",
                            },
                        },
                    },
                },
                "ResearchArtifact": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "schema_version",
                        "result_id",
                        "artifact",
                    ],
                    "properties": {
                        "schema_version": {
                            "type": "integer",
                            "const": 1,
                        },
                        "result_id": {
                            "type": "string",
                            "minLength": 1,
                        },
                        "artifact": {
                            "type": "object",
                            "additionalProperties": True,
                        },
                    },
                },
                "ResearchArtifactComparison": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "schema_version",
                        "artifact_a_result_id",
                        "artifact_b_result_id",
                        "comparison",
                    ],
                    "properties": {
                        "schema_version": {
                            "type": "integer",
                            "const": 1,
                        },
                        "artifact_a_result_id": {
                            "type": "string",
                            "minLength": 1,
                        },
                        "artifact_b_result_id": {
                            "type": "string",
                            "minLength": 1,
                        },
                        "comparison": {
                            "$ref": (
                                "#/components/schemas/"
                                "ArtifactComparison"
                            ),
                        },
                    },
                },
                "ArtifactComparison": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "artifact_a_id",
                        "artifact_b_id",
                        "hypothesis_evolution",
                        "evidence_evolution",
                        "confidence_evolution",
                    ],
                    "properties": {
                        "artifact_a_id": {
                            "type": "string",
                            "minLength": 1,
                        },
                        "artifact_b_id": {
                            "type": "string",
                            "minLength": 1,
                        },
                        "hypothesis_evolution": {
                            "$ref": (
                                "#/components/schemas/"
                                "HypothesisEvolution"
                            ),
                        },
                        "evidence_evolution": {
                            "$ref": (
                                "#/components/schemas/"
                                "EvidenceEvolution"
                            ),
                        },
                        "confidence_evolution": {
                            "$ref": (
                                "#/components/schemas/"
                                "ConfidenceEvolution"
                            ),
                        },
                    },
                },
                "HypothesisEvolution": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "previous_hypothesis",
                        "current_hypothesis",
                        "change_reason",
                    ],
                    "properties": {
                        "previous_hypothesis": {
                            "type": [
                                "string",
                                "null",
                            ],
                        },
                        "current_hypothesis": {
                            "type": "string",
                            "minLength": 1,
                        },
                        "change_reason": {
                            "type": [
                                "string",
                                "null",
                            ],
                        },
                    },
                },
                "EvidenceEvolution": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "previous_evidence",
                        "current_evidence",
                        "metric_deltas",
                        "change_reason",
                    ],
                    "properties": {
                        "previous_evidence": {
                            "type": [
                                "object",
                                "null",
                            ],
                            "additionalProperties": True,
                        },
                        "current_evidence": {
                            "type": "object",
                            "additionalProperties": True,
                        },
                        "metric_deltas": {
                            "type": "array",
                            "items": {
                                "$ref": (
                                    "#/components/schemas/"
                                    "EvidenceMetricDelta"
                                ),
                            },
                        },
                        "change_reason": {
                            "type": [
                                "string",
                                "null",
                            ],
                        },
                    },
                },
                "EvidenceMetricDelta": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "metric_name",
                        "previous_value",
                        "current_value",
                        "absolute_delta",
                        "direction",
                    ],
                    "properties": {
                        "metric_name": {
                            "type": "string",
                            "minLength": 1,
                        },
                        "previous_value": {},
                        "current_value": {},
                        "absolute_delta": {
                            "type": [
                                "number",
                                "null",
                            ],
                        },
                        "direction": {
                            "type": "string",
                            "enum": [
                                "increased",
                                "decreased",
                                "unchanged",
                                "added",
                                "removed",
                                "not_comparable",
                            ],
                        },
                    },
                },
                "ConfidenceEvolution": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "previous_confidence",
                        "current_confidence",
                        "change_reason",
                    ],
                    "properties": {
                        "previous_confidence": {
                            "type": "number",
                        },
                        "current_confidence": {
                            "type": "number",
                        },
                        "change_reason": {
                            "type": [
                                "string",
                                "null",
                            ],
                        },
                    },
                },
                "InvalidArtifactComparisonRequestError": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "schema_version",
                        "error",
                    ],
                    "properties": {
                        "schema_version": {
                            "type": "integer",
                            "const": 1,
                        },
                        "error": {
                            "type": "object",
                            "additionalProperties": False,
                            "required": [
                                "code",
                                "message",
                            ],
                            "properties": {
                                "code": {
                                    "type": "string",
                                    "const": (
                                        "invalid_artifact_"
                                        "comparison_request"
                                    ),
                                },
                                "message": {
                                    "type": "string",
                                    "minLength": 1,
                                },
                            },
                        },
                    },
                },
                "InvalidResearchArtifactComparisonError": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "schema_version",
                        "error",
                    ],
                    "properties": {
                        "schema_version": {
                            "type": "integer",
                            "const": 1,
                        },
                        "error": {
                            "type": "object",
                            "additionalProperties": False,
                            "required": [
                                "code",
                                "message",
                            ],
                            "properties": {
                                "code": {
                                    "type": "string",
                                    "const": (
                                        "research_artifact_"
                                        "comparison_invalid"
                                    ),
                                },
                                "message": {
                                    "type": "string",
                                    "minLength": 1,
                                },
                            },
                        },
                    },
                },                "ApiError": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "schema_version",
                        "error",
                    ],
                    "properties": {
                        "schema_version": {
                            "type": "integer",
                            "const": 1,
                        },
                        "error": {
                            "type": "object",
                            "additionalProperties": False,
                            "required": [
                                "code",
                                "message",
                            ],
                            "properties": {
                                "code": {
                                    "type": "string",
                                    "const": (
                                        "research_"
                                        "artifact_"
                                        "not_found"
                                    ),
                                },
                                "message": {
                                    "type": "string",
                                    "minLength": 1,
                                },
                            },
                        },
                    },
                },
            },
        },
    }

    if bearer_auth_required:
        components = document["components"]
        components["securitySchemes"] = {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
            },
        }
        components["schemas"][
            "UnauthorizedError"
        ] = {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "schema_version",
                "error",
            ],
            "properties": {
                "schema_version": {
                    "type": "integer",
                    "const": 1,
                },
                "error": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "code",
                        "message",
                    ],
                    "properties": {
                        "code": {
                            "type": "string",
                            "const": "unauthorized",
                        },
                        "message": {
                            "type": "string",
                            "minLength": 1,
                        },
                    },
                },
            },
        }
        document["security"] = [
            {"BearerAuth": []},
        ]

        for path_item in document["paths"].values():
            for operation in path_item.values():
                if operation.get("security") == []:
                    continue

                operation["responses"]["401"] = {
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

    return document