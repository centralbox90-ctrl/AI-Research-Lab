from __future__ import annotations

from flask import Flask, jsonify

from src.application.public_api import (
    GetStoredResearchArtifact,
    ListStoredResearchCycles,
)


def create_research_api(
    *,
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

    @application.get(
        "/v1/research-artifacts/<result_id>"
    )
    def get_research_artifact(
        result_id: str,
    ):
        artifact = (
            get_stored_research_artifact.execute(
                result_id
            )
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
        "/v1/research-cycles"
    )
    def list_research_cycles():
        result_ids = (
            list_stored_research_cycles.execute()
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