from __future__ import annotations


def build_openapi_document(
) -> dict[str, object]:
    """
    Build the versioned HTTP transport contract.

    The document describes transport DTOs only.
    Domain and persistence models are not exposed.
    """

    return {
        "openapi": "3.1.0",
        "info": {
            "title": "AI Research Lab API",
            "version": "1.0.0",
            "description": (
                "Read-only access to stored "
                "research results."
            ),
        },
        "paths": {
            "/v1/research-cycles": {
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
                "ApiError": {
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