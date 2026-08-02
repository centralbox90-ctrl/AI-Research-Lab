from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace

from flask import Flask

from app.research_submission import (
    MAX_SPECIFICATION_BYTES,
    create_research_submission_blueprint,
)
from app.web import (
    build_web_app,
    create_app,
)
from src.application import GetStoredResearchArtifact
from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
)
from src.storage import (
    SqliteExperimentExecutionRecorder,
    SqliteResearchCycleStore,
)


VALID_SPECIFICATION = {
    "executor_type": "market_backtest",
    "question_title": (
        "Does simple momentum predict forward returns?"
    ),
    "question_description": (
        "Evaluate a deterministic momentum signal."
    ),
    "hypothesis_title": (
        "Positive momentum precedes positive returns"
    ),
    "hypothesis_description": (
        "A positive momentum signal should be profitable."
    ),
    "expected_result": (
        "The backtest produces at least one completed trade."
    ),
    "experiment_title": "Browser research example",
    "experiment_description": (
        "Run one generated-data experiment from the browser."
    ),
    "data_source": "generated",
    "symbol": "EURUSD",
    "timeframe": "H1",
    "start_at": "2026-01-01T00:00:00Z",
    "end_at": "2026-07-01T00:00:00Z",
    "entry_rule": "simple positive momentum",
    "exit_rule": "configured risk and holding policy",
    "direction": "LONG",
    "stop_loss_percent": 1.0,
    "take_profit_percent": 2.0,
    "max_holding_bars": 10,
    "commission_percent": 0.0,
    "slippage_percent": 0.0,
    "strategy_parameters": {
        "signal_type": "simple_momentum",
    },
    "tags": [
        "browser",
        "example",
        "generated-data",
    ],
}


class FakeMarketResearchRunner:
    def __init__(self) -> None:
        self.specifications: list[
            MarketExperimentSpecification
        ] = []

    def execute(
        self,
        specification: MarketExperimentSpecification,
    ):
        self.specifications.append(specification)
        return SimpleNamespace(
            result=SimpleNamespace(
                id="result-browser-001",
            ),
        )


def build_test_app(
    runner: FakeMarketResearchRunner,
) -> Flask:
    application = Flask(__name__)
    application.config.update(
        TESTING=True,
        SECRET_KEY="test-secret",
    )

    @application.get("/", endpoint="index")
    def index():
        return "dashboard"

    @application.get(
        "/artifacts/<result_id>",
        endpoint="artifact_details",
    )
    def artifact_details(result_id: str):
        return result_id

    application.register_blueprint(
        create_research_submission_blueprint(
            runner=runner,
        )
    )
    return application


def get_csrf_token(client) -> str:
    response = client.get("/research/new")
    assert response.status_code == 200

    with client.session_transaction() as stored_session:
        token = stored_session[
            "research_submission_csrf_token"
        ]

    assert isinstance(token, str)
    assert token
    return token


def upload(
    client,
    *,
    token: str,
    source: bytes,
):
    return client.post(
        "/research",
        data={
            "csrf_token": token,
            "specification": (
                BytesIO(source),
                "research.json",
            ),
        },
        content_type="multipart/form-data",
    )


def test_valid_research_submission_runs_typed_specification():
    runner = FakeMarketResearchRunner()
    client = build_test_app(runner).test_client()
    token = get_csrf_token(client)

    response = upload(
        client,
        token=token,
        source=json.dumps(
            VALID_SPECIFICATION
        ).encode("utf-8"),
    )

    assert response.status_code == 303
    assert response.headers["Location"].endswith(
        "/artifacts/result-browser-001"
    )
    assert len(runner.specifications) == 1
    assert isinstance(
        runner.specifications[0],
        MarketExperimentSpecification,
    )
    assert runner.specifications[0].symbol == "EURUSD"


def test_research_submission_rejects_invalid_csrf_token():
    runner = FakeMarketResearchRunner()
    client = build_test_app(runner).test_client()
    get_csrf_token(client)

    response = upload(
        client,
        token="wrong-token",
        source=json.dumps(
            VALID_SPECIFICATION
        ).encode("utf-8"),
    )

    assert response.status_code == 400
    assert runner.specifications == []


def test_research_submission_rejects_invalid_json():
    runner = FakeMarketResearchRunner()
    client = build_test_app(runner).test_client()
    token = get_csrf_token(client)

    response = upload(
        client,
        token=token,
        source=b"{",
    )

    assert response.status_code == 400
    assert b"Invalid specification JSON" in response.data
    assert runner.specifications == []


def test_research_submission_rejects_invalid_contract():
    runner = FakeMarketResearchRunner()
    client = build_test_app(runner).test_client()
    token = get_csrf_token(client)

    response = upload(
        client,
        token=token,
        source=json.dumps(
            {
                "executor_type": "market_backtest",
            }
        ).encode("utf-8"),
    )

    assert response.status_code == 422
    assert b"missing specification fields" in response.data
    assert runner.specifications == []


def test_research_submission_rejects_oversized_file():
    runner = FakeMarketResearchRunner()
    client = build_test_app(runner).test_client()
    token = get_csrf_token(client)

    response = upload(
        client,
        token=token,
        source=b"x" * (
            MAX_SPECIFICATION_BYTES + 1
        ),
    )

    assert response.status_code == 413
    assert runner.specifications == []


def test_dashboard_registers_research_submission_when_configured():
    runner = FakeMarketResearchRunner()
    application = create_app(
        research_runner=runner,
        secret_key="test-secret",
    )
    client = application.test_client()

    dashboard = client.get("/")
    form = client.get("/research/new")

    assert dashboard.status_code == 200
    assert b"/research/new" in dashboard.data
    assert form.status_code == 200


def test_build_web_app_runs_persists_and_reopens_research(
    tmp_path: Path,
):
    database_path = tmp_path / "browser.db"
    application = build_web_app(
        db_path=database_path,
    )
    client = application.test_client()
    token = get_csrf_token(client)

    example_path = (
        Path(__file__).resolve().parents[1]
        / "examples"
        / "market_research_specification.json"
    )

    response = upload(
        client,
        token=token,
        source=example_path.read_bytes(),
    )

    assert response.status_code == 303

    result_id = response.headers["Location"].rsplit(
        "/",
        1,
    )[-1]

    details = client.get(
        response.headers["Location"]
    )
    dashboard = client.get("/")

    reopened_store = SqliteResearchCycleStore(
        db_path=database_path,
    )
    artifact = GetStoredResearchArtifact(
        store=reopened_store,
    ).execute(result_id)

    execution_recorder = (
        SqliteExperimentExecutionRecorder(
            db_path=database_path,
        )
    )
    execution_ids = (
        execution_recorder.list_execution_ids()
    )

    assert details.status_code == 200
    assert dashboard.status_code == 200
    assert artifact is not None
    assert artifact["artifact_type"] == (
        "market_research_cycle"
    )
    assert b"EURUSD" in dashboard.data
    assert b"H1" in dashboard.data
    assert b"Unknown symbol" not in dashboard.data
    assert b"market_backtest" in details.data
    assert (
        b"Evaluate a deterministic momentum signal on generated market data."
        in details.data
    )

    artifact_id = artifact["artifact_id"]
    assert isinstance(artifact_id, str)
    assert artifact_id.encode("utf-8") in details.data
    assert len(execution_ids) == 1

    history = execution_recorder.history(
        execution_ids[0]
    )

    assert [
        snapshot.status.value
        for snapshot in history
    ] == [
        "PENDING",
        "RUNNING",
        "SUCCEEDED",
    ]
    assert history[-1].result_id == result_id
