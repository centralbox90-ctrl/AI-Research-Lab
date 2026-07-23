from __future__ import annotations

import json
from datetime import UTC, datetime

import pytest

import app.run_mt5_indicator_comparative_research as runner
from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
)
from src.research.outcome_specification import (
    ForwardReturnSpecification,
)


def build_cli_arguments() -> list[str]:
    return [
        "--indicator",
        "rsi",
        "--symbol",
        " eurusd ",
        "--timeframe",
        " h1 ",
        "--start-at",
        "2026-01-01T00:00:00Z",
        "--end-at",
        "2026-02-01T00:00:00+00:00",
        "--horizon",
        "1",
        "--horizon",
        "3",
    ]


def test_parses_comparative_research_arguments(
) -> None:
    arguments = runner.parse_arguments(
        build_cli_arguments()
    )
    specification = (
        runner.build_market_specification(
            arguments
        )
    )

    assert isinstance(
        specification,
        MarketExperimentSpecification,
    )
    assert specification.symbol == "EURUSD"
    assert specification.timeframe == "H1"
    assert specification.start_at == datetime(
        2026,
        1,
        1,
        tzinfo=UTC,
    )
    assert specification.end_at == datetime(
        2026,
        2,
        1,
        tzinfo=UTC,
    )
    assert arguments.horizons == [1, 3]


def test_uses_default_horizons() -> None:
    arguments = runner.parse_arguments(
        [
            "--symbol",
            "EURUSD",
            "--start-at",
            "2026-01-01T00:00:00+00:00",
            "--end-at",
            "2026-02-01T00:00:00+00:00",
        ]
    )

    assert arguments.indicator == "rsi"
    assert arguments.timeframe == "H1"
    assert arguments.horizons == [1, 3, 5]


def test_builds_application_with_canonical_mt5_provider(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    raw_provider = object()
    canonical_provider = object()
    expected_application = object()
    captured: dict[str, object] = {}

    monkeypatch.setattr(
        runner,
        "Mt5MarketDataProvider",
        lambda: raw_provider,
    )

    def build_canonical_provider(
        provider: object,
    ) -> object:
        captured["raw_provider"] = provider
        return canonical_provider

    def build_application(
        *,
        data_provider: object,
    ) -> object:
        captured["data_provider"] = data_provider
        return expected_application

    monkeypatch.setattr(
        runner,
        "CanonicalMarketDataProvider",
        build_canonical_provider,
    )
    monkeypatch.setattr(
        runner,
        (
            "build_default_indicator_"
            "comparative_research_application"
        ),
        build_application,
    )

    application = runner.build_application()

    assert application is expected_application
    assert captured == {
        "raw_provider": raw_provider,
        "data_provider": canonical_provider,
    }


def test_executes_application_and_presents_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expected_result = object()
    expected_payload = {
        "status": "presented",
    }

    class StubApplication:
        def __init__(self) -> None:
            self.arguments: dict[
                str,
                object,
            ] | None = None

        def run(
            self,
            **arguments: object,
        ) -> object:
            self.arguments = arguments
            return expected_result

    application = StubApplication()

    monkeypatch.setattr(
        runner,
        (
            "present_indicator_comparative_"
            "research_result"
        ),
        lambda result: (
            expected_payload
            if result is expected_result
            else pytest.fail(
                "Unexpected result was presented"
            )
        ),
    )

    arguments = runner.parse_arguments(
        build_cli_arguments()
    )
    payload = runner.execute_comparative_research(
        arguments=arguments,
        application=application,
    )

    assert payload == expected_payload
    assert application.arguments is not None
    assert application.arguments[
        "indicator_id"
    ] == "rsi"

    market_specification = application.arguments[
        "market_specification"
    ]
    outcome_specification = application.arguments[
        "outcome_specification"
    ]

    assert isinstance(
        market_specification,
        MarketExperimentSpecification,
    )
    assert isinstance(
        outcome_specification,
        ForwardReturnSpecification,
    )
    assert outcome_specification.horizons == (
        1,
        3,
    )


def test_main_prints_json(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    expected_payload = {
        "indicator": {
            "id": "rsi",
        },
    }

    monkeypatch.setattr(
        runner,
        "build_application",
        lambda: object(),
    )
    monkeypatch.setattr(
        runner,
        "execute_comparative_research",
        lambda **arguments: (
            expected_payload
         ),
    )

    exit_code = runner.main(
        build_cli_arguments()
    )
    output = json.loads(
        capsys.readouterr().out
    )

    assert exit_code == 0
    assert output == expected_payload
