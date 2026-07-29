from __future__ import annotations

from flask import Flask, jsonify

from src.application.public_api import (
    ListStoredResearchCycles,
)


def create_research_api(
    *,
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