from __future__ import annotations

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

    application = Flask(__name__)

    @application.get("/openapi.json")
    def get_openapi_document():
        return jsonify(
            build_openapi_document()
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