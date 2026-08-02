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
    <link
        rel="stylesheet"
        href="{{ url_for('static', filename='research_lab.css') }}"
    >
</head>
<body>
    <main>
        <p><a href="{{ url_for('index') }}">← Dashboard</a></p>
        <h1>Run market research</h1>
        <p>
            Describe one reproducible generated-data market
            experiment. The submitted values are validated through
            the strict MarketExperimentSpecification contract.
        </p>

        {% if error %}
            <p role="alert">{{ error }}</p>
        {% endif %}

        <section>
            <h2>Research specification</h2>
            <form
                class="research-entry-form"
                action="{{
                    url_for(
                        'research_submission.submit_research_form'
                    )
                }}"
                method="post"
            >
                <input
                    type="hidden"
                    name="csrf_token"
                    value="{{ csrf_token }}"
                >

                <fieldset>
                    <legend>Research question</legend>
                    <div class="research-form-grid">
                        <p class="form-field-wide">
                            <label for="question_title">
                                Question
                            </label>
                            <input
                                id="question_title"
                                name="question_title"
                                type="text"
                                value="{{
                                    form_data.get(
                                        'question_title',
                                        'Does simple momentum predict forward returns?'
                                    )
                                }}"
                                required
                            >
                        </p>
                        <p class="form-field-wide">
                            <label for="question_description">
                                Question description
                            </label>
                            <textarea
                                id="question_description"
                                name="question_description"
                                rows="3"
                                required
                            >{{ form_data.get(
                                'question_description',
                                'Evaluate a deterministic momentum signal on generated market data.'
                            ) }}</textarea>
                        </p>
                    </div>
                </fieldset>

                <fieldset>
                    <legend>Hypothesis</legend>
                    <div class="research-form-grid">
                        <p class="form-field-wide">
                            <label for="hypothesis_title">
                                Hypothesis
                            </label>
                            <input
                                id="hypothesis_title"
                                name="hypothesis_title"
                                type="text"
                                value="{{
                                    form_data.get(
                                        'hypothesis_title',
                                        'Positive momentum precedes positive returns'
                                    )
                                }}"
                                required
                            >
                        </p>
                        <p class="form-field-wide">
                            <label for="hypothesis_description">
                                Hypothesis description
                            </label>
                            <textarea
                                id="hypothesis_description"
                                name="hypothesis_description"
                                rows="3"
                                required
                            >{{ form_data.get(
                                'hypothesis_description',
                                'A positive momentum signal should be profitable.'
                            ) }}</textarea>
                        </p>
                        <p class="form-field-wide">
                            <label for="expected_result">
                                Expected result
                            </label>
                            <textarea
                                id="expected_result"
                                name="expected_result"
                                rows="2"
                                required
                            >{{ form_data.get(
                                'expected_result',
                                'The backtest produces at least one completed trade.'
                            ) }}</textarea>
                        </p>
                    </div>
                </fieldset>

                <fieldset>
                    <legend>Experiment and generated data</legend>
                    <div class="research-form-grid">
                        <p class="form-field-wide">
                            <label for="experiment_title">
                                Experiment title
                            </label>
                            <input
                                id="experiment_title"
                                name="experiment_title"
                                type="text"
                                value="{{
                                    form_data.get(
                                        'experiment_title',
                                        'Browser research example'
                                    )
                                }}"
                                required
                            >
                        </p>
                        <p class="form-field-wide">
                            <label for="experiment_description">
                                Experiment description
                            </label>
                            <textarea
                                id="experiment_description"
                                name="experiment_description"
                                rows="3"
                                required
                            >{{ form_data.get(
                                'experiment_description',
                                'Run one generated-data experiment from the browser.'
                            ) }}</textarea>
                        </p>
                        <p>
                            <label for="symbol">Symbol</label>
                            <input
                                id="symbol"
                                name="symbol"
                                type="text"
                                value="{{
                                    form_data.get('symbol', 'EURUSD')
                                }}"
                                required
                            >
                        </p>
                        <p>
                            <label for="timeframe">Timeframe</label>
                            <input
                                id="timeframe"
                                name="timeframe"
                                type="text"
                                value="{{
                                    form_data.get('timeframe', 'H1')
                                }}"
                                required
                            >
                        </p>
                        <p>
                            <label for="start_at">Start time (UTC)</label>
                            <input
                                id="start_at"
                                name="start_at"
                                type="datetime-local"
                                value="{{
                                    form_data.get(
                                        'start_at',
                                        '2026-01-01T00:00'
                                    )
                                }}"
                                required
                            >
                        </p>
                        <p>
                            <label for="end_at">End time (UTC)</label>
                            <input
                                id="end_at"
                                name="end_at"
                                type="datetime-local"
                                value="{{
                                    form_data.get(
                                        'end_at',
                                        '2026-07-01T00:00'
                                    )
                                }}"
                                required
                            >
                        </p>
                        <p class="form-field-wide">
                            <label for="entry_rule">Entry rule</label>
                            <input
                                id="entry_rule"
                                name="entry_rule"
                                type="text"
                                value="{{
                                    form_data.get(
                                        'entry_rule',
                                        'simple positive momentum'
                                    )
                                }}"
                                required
                            >
                        </p>
                        <p class="form-field-wide">
                            <label for="exit_rule">Exit rule</label>
                            <input
                                id="exit_rule"
                                name="exit_rule"
                                type="text"
                                value="{{
                                    form_data.get(
                                        'exit_rule',
                                        'configured risk and holding policy'
                                    )
                                }}"
                                required
                            >
                        </p>
                    </div>
                </fieldset>

                <fieldset>
                    <legend>Direction, risk, and costs</legend>
                    <div class="research-form-grid">
                        {% set selected_direction = form_data.get(
                            'direction',
                            'LONG'
                        ) %}
                        <p>
                            <label for="direction">Direction</label>
                            <select
                                id="direction"
                                name="direction"
                                required
                            >
                                <option
                                    value="LONG"
                                    {% if selected_direction == 'LONG' %}
                                        selected
                                    {% endif %}
                                >Long</option>
                                <option
                                    value="SHORT"
                                    {% if selected_direction == 'SHORT' %}
                                        selected
                                    {% endif %}
                                >Short</option>
                            </select>
                        </p>
                        <p>
                            <label for="max_holding_bars">
                                Maximum holding bars
                            </label>
                            <input
                                id="max_holding_bars"
                                name="max_holding_bars"
                                type="number"
                                min="1"
                                step="1"
                                value="{{
                                    form_data.get(
                                        'max_holding_bars',
                                        '10'
                                    )
                                }}"
                                required
                            >
                        </p>
                        <p>
                            <label for="stop_loss_percent">
                                Stop loss (%)
                            </label>
                            <input
                                id="stop_loss_percent"
                                name="stop_loss_percent"
                                type="number"
                                min="0.0001"
                                step="any"
                                value="{{
                                    form_data.get(
                                        'stop_loss_percent',
                                        '1.0'
                                    )
                                }}"
                                required
                            >
                        </p>
                        <p>
                            <label for="take_profit_percent">
                                Take profit (%)
                            </label>
                            <input
                                id="take_profit_percent"
                                name="take_profit_percent"
                                type="number"
                                min="0.0001"
                                step="any"
                                value="{{
                                    form_data.get(
                                        'take_profit_percent',
                                        '2.0'
                                    )
                                }}"
                                required
                            >
                        </p>
                        <p>
                            <label for="commission_percent">
                                Commission (%)
                            </label>
                            <input
                                id="commission_percent"
                                name="commission_percent"
                                type="number"
                                min="0"
                                step="0.001"
                                value="{{
                                    form_data.get(
                                        'commission_percent',
                                        '0.0'
                                    )
                                }}"
                                required
                            >
                        </p>
                        <p>
                            <label for="slippage_percent">
                                Slippage (%)
                            </label>
                            <input
                                id="slippage_percent"
                                name="slippage_percent"
                                type="number"
                                min="0"
                                step="0.001"
                                value="{{
                                    form_data.get(
                                        'slippage_percent',
                                        '0.0'
                                    )
                                }}"
                                required
                            >
                        </p>
                    </div>
                </fieldset>

                <p class="form-actions">
                    <button type="submit">Run research</button>
                </p>
            </form>

            <details class="advanced-upload">
                <summary>
                    Advanced: upload JSON specification
                </summary>
                <p>
                    Upload one UTF-8 JSON document that follows the
                    same strict MarketExperimentSpecification
                    contract.
                </p>
                <form
                    action="{{
                        url_for(
                            'research_submission.submit_research'
                        )
                    }}"
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
                            JSON research specification
                        </label>
                        <input
                            id="specification"
                            name="specification"
                            type="file"
                            accept=".json,application/json"
                            required
                        >
                    </p>
                    <button type="submit">
                        Run JSON specification
                    </button>
                </form>
            </details>
        </section>
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
                form_data=request.form,
            ),
            status_code,
        )

    def execute_payload(payload: Any):
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

        return execute_payload(payload)

    @blueprint.post("/research/form")
    def submit_research_form():
        if not _has_valid_csrf_token():
            return render_form(
                error="The research form expired. Try again.",
                status_code=400,
            )

        try:
            payload = _build_form_payload()
        except (TypeError, ValueError) as error:
            return render_form(
                error=str(error),
                status_code=422,
            )

        return execute_payload(payload)

    return blueprint


def _build_form_payload() -> dict[str, Any]:
    return {
        "executor_type": "market_backtest",
        "question_title": _required_form_text(
            "question_title"
        ),
        "question_description": _required_form_text(
            "question_description"
        ),
        "hypothesis_title": _required_form_text(
            "hypothesis_title"
        ),
        "hypothesis_description": _required_form_text(
            "hypothesis_description"
        ),
        "expected_result": _required_form_text(
            "expected_result"
        ),
        "experiment_title": _required_form_text(
            "experiment_title"
        ),
        "experiment_description": _required_form_text(
            "experiment_description"
        ),
        "data_source": "generated",
        "symbol": _required_form_text("symbol"),
        "timeframe": _required_form_text(
            "timeframe"
        ),
        "start_at": _form_datetime("start_at"),
        "end_at": _form_datetime("end_at"),
        "entry_rule": _required_form_text(
            "entry_rule"
        ),
        "exit_rule": _required_form_text(
            "exit_rule"
        ),
        "direction": _required_form_text(
            "direction"
        ),
        "stop_loss_percent": _form_float(
            "stop_loss_percent"
        ),
        "take_profit_percent": _form_float(
            "take_profit_percent"
        ),
        "max_holding_bars": _form_integer(
            "max_holding_bars"
        ),
        "commission_percent": _form_float(
            "commission_percent"
        ),
        "slippage_percent": _form_float(
            "slippage_percent"
        ),
        "strategy_parameters": {
            "signal_type": "simple_momentum",
        },
        "tags": [
            "browser",
            "generated-data",
        ],
    }


def _required_form_text(field_name: str) -> str:
    value = request.form.get(field_name)

    if (
        not isinstance(value, str)
        or not value.strip()
    ):
        readable_name = field_name.replace(
            "_",
            " ",
        )
        raise ValueError(
            f"{readable_name} is required"
        )

    return value.strip()


def _form_datetime(field_name: str) -> str:
    value = _required_form_text(field_name)

    if len(value) == 16:
        return f"{value}:00Z"

    if len(value) == 19:
        return f"{value}Z"

    return value


def _form_float(field_name: str) -> float:
    value = _required_form_text(field_name)

    try:
        return float(value)
    except ValueError:
        readable_name = field_name.replace(
            "_",
            " ",
        )
        raise ValueError(
            f"{readable_name} must be a number"
        ) from None


def _form_integer(field_name: str) -> int:
    value = _required_form_text(field_name)

    try:
        return int(value)
    except ValueError:
        readable_name = field_name.replace(
            "_",
            " ",
        )
        raise ValueError(
            f"{readable_name} must be an integer"
        ) from None


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
