from __future__ import annotations

import json
from hmac import compare_digest
from json import JSONDecodeError
from secrets import token_urlsafe
from typing import Any, Protocol

from flask import (
    Blueprint,
    abort,
    redirect,
    render_template_string,
    request,
    session,
    url_for,
)

from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
)
from src.application.market_experiment_specification_loader import (
    MarketExperimentSpecificationLoader,
)


MAX_SPECIFICATION_BYTES = 64 * 1024
_CSRF_SESSION_KEY = "research_submission_csrf_token"

RESEARCH_FORM_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Run market research · AI Research Lab</title>
</head>
<body>
    <main>
        <p><a href="{{ url_for('index') }}">← Dashboard</a></p>
        <h1>Run market research</h1>
        <p>
            Upload one UTF-8 JSON document that follows the strict
            MarketExperimentSpecification contract.
        </p>

        {% if error %}
            <p role="alert">{{ error }}</p>
        {% endif %}

        <form
            action="{{ url_for('research_submission.submit_research') }}"
            method="post"
            enctype="multipart/form-data"
        >
            <input
                type="hidden"
                name="csrf_token"
                value="{{ csrf_token }}"
            >

            <p>
                <label for="specification">
                    Research specification
                </label>
                <input
                    id="specification"
                    name="specification"
                    type="file"
                    accept=".json,application/json"
                    required
                >
            </p>

            <button type="submit">Run research</button>
        </form>
    </main>
</body>
</html>
"""


class MarketResearchRunner(Protocol):
    def execute(
        self,
        specification: MarketExperimentSpecification,
    ) -> Any:
        ...


def create_research_submission_blueprint(
    *,
    runner: MarketResearchRunner,
    loader: MarketExperimentSpecificationLoader | None = None,
) -> Blueprint:
    if not callable(getattr(runner, "execute", None)):
        raise TypeError(
            "runner must provide a callable execute method"
        )

    if (
        loader is not None
        and not isinstance(
            loader,
            MarketExperimentSpecificationLoader,
        )
    ):
        raise TypeError(
            "loader must be a "
            "MarketExperimentSpecificationLoader or None"
        )

    specification_loader = (
        loader
        or MarketExperimentSpecificationLoader()
    )
    blueprint = Blueprint(
        "research_submission",
        __name__,
    )

    def render_form(
        *,
        error: str | None = None,
        status_code: int = 200,
    ):
        return (
            render_template_string(
                RESEARCH_FORM_TEMPLATE,
                error=error,
                csrf_token=_get_csrf_token(),
            ),
            status_code,
        )

    @blueprint.get("/research/new")
    def new_research():
        return render_form()

    @blueprint.post("/research")
    def submit_research():
        if not _has_valid_csrf_token():
            return render_form(
                error="The research form expired. Try again.",
                status_code=400,
            )

        uploaded = request.files.get(
            "specification"
        )

        if (
            uploaded is None
            or not uploaded.filename
        ):
            return render_form(
                error=(
                    "Select a JSON research "
                    "specification file."
                ),
                status_code=400,
            )

        source = uploaded.stream.read(
            MAX_SPECIFICATION_BYTES + 1
        )

        if len(source) > MAX_SPECIFICATION_BYTES:
            abort(413)

        try:
            decoded = source.decode("utf-8-sig")
        except UnicodeDecodeError:
            return render_form(
                error=(
                    "Research specification must "
                    "use UTF-8 encoding."
                ),
                status_code=400,
            )

        try:
            payload = json.loads(decoded)
        except JSONDecodeError as error:
            return render_form(
                error=(
                    "Invalid specification JSON: "
                    f"{error.msg}."
                ),
                status_code=400,
            )

        try:
            specification = (
                specification_loader.from_dict(
                    payload
                )
            )
            result = runner.execute(specification)
        except (
            TypeError,
            ValueError,
            LookupError,
            RuntimeError,
        ) as error:
            return render_form(
                error=str(error),
                status_code=422,
            )

        research_result = getattr(
            result,
            "result",
            None,
        )
        result_id = getattr(
            research_result,
            "id",
            None,
        )

        if (
            not isinstance(result_id, str)
            or not result_id.strip()
        ):
            raise TypeError(
                "market research result must "
                "provide a non-empty result id"
            )

        session.pop(
            _CSRF_SESSION_KEY,
            None,
        )

        return redirect(
            url_for(
                "artifact_details",
                result_id=result_id,
            ),
            code=303,
        )

    return blueprint


def _get_csrf_token() -> str:
    token = session.get(
        _CSRF_SESSION_KEY
    )

    if (
        not isinstance(token, str)
        or not token
    ):
        token = token_urlsafe(32)
        session[_CSRF_SESSION_KEY] = token

    return token


def _has_valid_csrf_token() -> bool:
    expected = session.get(
        _CSRF_SESSION_KEY
    )
    provided = request.form.get(
        "csrf_token"
    )

    if (
        not isinstance(expected, str)
        or not expected
        or not isinstance(provided, str)
        or not provided
    ):
        return False

    return compare_digest(
        provided.encode("utf-8"),
        expected.encode("utf-8"),
    )
