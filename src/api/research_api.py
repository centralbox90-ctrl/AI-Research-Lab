from __future__ import annotations

from hmac import compare_digest

from flask import Flask, jsonify, request

from src.api.openapi import (
    build_openapi_document,
)
from src.application.public_api import (
    CompareStoredResearchArtifacts,
    GetStoredResearchArtifact,
    ListStoredResearchCycles,
    StoredResearchArtifactIntegrityError,
)


def _stored_artifact_integrity_response(
    error: StoredResearchArtifactIntegrityError,
):
    return (
        jsonify(
            {
                "schema_version": 1,
                "error": {
                    "code": (
                        "stored_research_artifact_"
                        "integrity_error"
                    ),
                    "message": str(error),
                    "result_id": error.result_id,
                    "reason": error.reason,
                },
            }
        ),
        422,
    )


def _unauthorized_response():
    response = jsonify(
        {
            "schema_version": 1,
            "error": {
                "code": "unauthorized",
                "message": (
                    "A valid Bearer token is required."
                ),
            },
        }
    )
    response.status_code = 401
    response.headers["WWW-Authenticate"] = (
        'Bearer realm="ai-research-lab"'
    )

    return response


def create_research_api(
    *,
    compare_stored_research_artifacts: (
        CompareStoredResearchArtifacts
    ),
    get_stored_research_artifact: (
        GetStoredResearchArtifact
    ),
    list_stored_research_cycles: (
        ListStoredResearchCycles
    ),
    api_token: str | None = None,
    readiness_check: Callable[[], bool] | None = None,
) -> Flask:
    """
    Create the HTTP adapter for public research use cases.

    The adapter owns transport routing and DTO rendering.
    It does not construct persistence or domain dependencies.
    """

    if not callable(
        getattr(
            compare_stored_research_artifacts,
            "execute",
            None,
        )
    ):
        raise TypeError(
            "compare_stored_research_artifacts must provide "
            "a callable execute method"
        )

    if not callable(
        getattr(
            get_stored_research_artifact,
            "execute",
            None,
        )
    ):
        raise TypeError(
            "get_stored_research_artifact must provide "
            "a callable execute method"
        )

    if not callable(
        getattr(
            list_stored_research_cycles,
            "execute",
            None,
        )
    ):
        raise TypeError(
            "list_stored_research_cycles must provide "
            "a callable execute method"
        )

    if (
        readiness_check is not None
        and not callable(readiness_check)
    ):
        raise TypeError(
            "readiness_check must be callable or None"
        )

    if api_token is not None:
        if not isinstance(api_token, str):
            raise TypeError(
                "api_token must be a string or None"
            )

        if not api_token.strip():
            raise ValueError(
                "api_token must not be empty"
            )

        if api_token != api_token.strip():
            raise ValueError(
                "api_token must not contain "
                "surrounding whitespace"
            )

    expected_api_token = (
        api_token.encode("utf-8")
        if api_token is not None
        else None
    )

    application = Flask(__name__)

    @application.before_request
    def require_api_token():
        if request.path in {
            "/health",
            "/ready",
        }:
            return None

        if expected_api_token is None:
            return None

        authorization = request.headers.get(
            "Authorization",
            "",
        )
        (
            scheme,
            separator,
            provided_token,
        ) = authorization.partition(" ")

        if (
            separator != " "
            or scheme.casefold() != "bearer"
            or not provided_token
        ):
            return _unauthorized_response()

        if not compare_digest(
            provided_token.encode("utf-8"),
            expected_api_token,
        ):
            return _unauthorized_response()

        return None

    @application.get("/health")
    def get_health():
        return jsonify(
            {
                "schema_version": 1,
                "status": "healthy",
            }
        )

    @application.get("/ready")
    def get_readiness():
        try:
            is_ready = (
                readiness_check is not None
                and readiness_check() is True
            )
        except Exception:
            is_ready = False

        if not is_ready:
            return (
                jsonify(
                    {
                        "schema_version": 1,
                        "error": {
                            "code": (
                                "service_unavailable"
                            ),
                            "message": (
                                "The service is not ready."
                            ),
                        },
                    }
                ),
                503,
            )

        return jsonify(
            {
                "schema_version": 1,
                "status": "ready",
            }
        )

    @application.get("/openapi.json")
    def get_openapi_document():
        return jsonify(
            build_openapi_document(
                bearer_auth_required=(
                    api_token is not None
                )
            )
        )

    @application.get(
        "/v1/research-artifacts/<result_id>"
    )
    def get_research_artifact(
        result_id: str,
    ):
        try:
            artifact = (
                get_stored_research_artifact.execute(
                    result_id
                )
            )
        except StoredResearchArtifactIntegrityError as error:
            return _stored_artifact_integrity_response(
                error
            )

        if artifact is None:
            return (
                jsonify(
                    {
                        "schema_version": 1,
                        "error": {
                            "code": (
                                "research_artifact_not_found"
                            ),
                            "message": (
                                "Research artifact not found: "
                                + result_id
                            ),
                        },
                    }
                ),
                404,
            )

        if not isinstance(artifact, dict):
            raise TypeError(
                "GetStoredResearchArtifact must return "
                "a dictionary or None"
            )

        return jsonify(
            {
                "schema_version": 1,
                "result_id": result_id,
                "artifact": artifact,
            }
        )

    @application.get(
        "/v1/research-artifact-comparisons"
    )
    def compare_research_artifacts():
        artifact_a_result_id = request.args.get(
            "artifact_a_result_id"
        )
        artifact_b_result_id = request.args.get(
            "artifact_b_result_id"
        )

        if (
            not isinstance(
                artifact_a_result_id,
                str,
            )
            or not artifact_a_result_id.strip()
            or not isinstance(
                artifact_b_result_id,
                str,
            )
            or not artifact_b_result_id.strip()
        ):
            return (
                jsonify(
                    {
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
                ),
                400,
            )

        artifact_a_result_id = (
            artifact_a_result_id.strip()
        )
        artifact_b_result_id = (
            artifact_b_result_id.strip()
        )

        try:
            comparison = (
                compare_stored_research_artifacts.execute(
                    artifact_a_result_id=(
                        artifact_a_result_id
                    ),
                    artifact_b_result_id=(
                        artifact_b_result_id
                    ),
                )
            )
        except ValueError as error:
            message = str(error)

            if message.startswith(
                "Research artifact was not found "
                "for result_id: "
            ):
                status_code = 404
                error_code = (
                    "research_artifact_not_found"
                )
            else:
                status_code = 422
                error_code = (
                    "research_artifact_comparison_invalid"
                )

            return (
                jsonify(
                    {
                        "schema_version": 1,
                        "error": {
                            "code": error_code,
                            "message": message,
                        },
                    }
                ),
                status_code,
            )

        return jsonify(
            {
                "schema_version": 1,
                "artifact_a_result_id": (
                    artifact_a_result_id
                ),
                "artifact_b_result_id": (
                    artifact_b_result_id
                ),
                "comparison": {
                    "artifact_a_id": (
                        comparison.artifact_a_id
                    ),
                    "artifact_b_id": (
                        comparison.artifact_b_id
                    ),
                    "hypothesis_evolution": {
                        "previous_hypothesis": (
                            comparison
                            .hypothesis_evolution
                            .previous_hypothesis
                        ),
                        "current_hypothesis": (
                            comparison
                            .hypothesis_evolution
                            .current_hypothesis
                        ),
                        "change_reason": (
                            comparison
                            .hypothesis_evolution
                            .change_reason
                        ),
                    },
                    "evidence_evolution": {
                        "previous_evidence": (
                            comparison
                            .evidence_evolution
                            .previous_evidence
                        ),
                        "current_evidence": (
                            comparison
                            .evidence_evolution
                            .current_evidence
                        ),
                        "metric_deltas": [
                            {
                                "metric_name": (
                                    delta.metric_name
                                ),
                                "previous_value": (
                                    delta.previous_value
                                ),
                                "current_value": (
                                    delta.current_value
                                ),
                                "absolute_delta": (
                                    delta.absolute_delta
                                ),
                                "direction": (
                                    delta.direction
                                ),
                            }
                            for delta in (
                                comparison
                                .evidence_evolution
                                .metric_deltas
                            )
                        ],
                        "change_reason": (
                            comparison
                            .evidence_evolution
                            .change_reason
                        ),
                    },
                    "confidence_evolution": {
                        "previous_confidence": (
                            comparison
                            .confidence_evolution
                            .previous_confidence
                        ),
                        "current_confidence": (
                            comparison
                            .confidence_evolution
                            .current_confidence
                        ),
                        "change_reason": (
                            comparison
                            .confidence_evolution
                            .change_reason
                        ),
                    },
                },
            }
        )
    @application.get(
        "/v1/research-cycles"
    )
    def list_research_cycles():
        try:
            result_ids = (
                list_stored_research_cycles.execute()
            )
        except StoredResearchArtifactIntegrityError as error:
            return _stored_artifact_integrity_response(
                error
            )

        if not isinstance(result_ids, list):
            raise TypeError(
                "ListStoredResearchCycles must return "
                "a list"
            )

        if not all(
            isinstance(result_id, str)
            for result_id in result_ids
        ):
            raise TypeError(
                "research cycle identifiers "
                "must be strings"
            )

        return jsonify(
            {
                "schema_version": 1,
                "count": len(result_ids),
                "result_ids": result_ids,
            }
        )

    return application