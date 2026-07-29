from datetime import datetime, timezone

import pytest

from src.application.hypothesis_evaluation_application import (
    HypothesisEvaluationApplication,
)
from src.application.indicator_comparative_finding_application import (
    IndicatorComparativeFindingApplication,
)
from src.application.indicator_comparative_hypothesis_evaluation_application import (
    IndicatorComparativeFindingRequest,
    IndicatorComparativeHypothesisEvaluationApplication,
)
from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
    MarketPositionDirection,
)
from src.research.finding import (
    Finding,
    FindingRelationship,
)
from src.research.hypothesis_evaluation import (
    HypothesisEvaluation,
    HypothesisEvaluationState,
)
from src.research.outcome_specification import (
    ForwardReturnSpecification,
)


def build_market_specification(
) -> MarketExperimentSpecification:
    return MarketExperimentSpecification(
        executor_type="market_backtest",
        question_title="RSI question",
        question_description="RSI research question",
        hypothesis_title="RSI hypothesis",
        hypothesis_description="RSI effect",
        expected_result="Positive effect",
        experiment_title="RSI experiment",
        experiment_description="Evaluate RSI",
        data_source="generated",
        symbol="EURUSD",
        timeframe="H1",
        start_at=datetime(
            2026,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        end_at=datetime(
            2026,
            2,
            1,
            tzinfo=timezone.utc,
        ),
        entry_rule="rsi < 30",
        exit_rule="rsi > 50",
        direction=MarketPositionDirection.LONG,
        stop_loss_percent=1.0,
        take_profit_percent=2.0,
        max_holding_bars=10,
    )


def build_request(
    *,
    horizon: int = 1,
    indicator_id: str = "rsi",
) -> IndicatorComparativeFindingRequest:
    return IndicatorComparativeFindingRequest(
        market_specifications=(
            build_market_specification(),
        ),
        indicator_id=indicator_id,
        outcome_specification=(
            ForwardReturnSpecification(
                horizons=(1, 3),
            )
        ),
        horizon=horizon,
        statement=(
            f"{indicator_id} finding at "
            f"horizon {horizon}."
        ),
        applicable_markets=(
            "EURUSD:H1",
        ),
    )


def build_finding(
    finding_id: str,
) -> Finding:
    return Finding(
        id=finding_id,
        hypothesis_id="hypothesis-rsi",
        statement=f"{finding_id} statement.",
        relationship=FindingRelationship.SUPPORTING,
        confidence=0.8,
        applicable_markets=(
            "EURUSD:H1",
        ),
        limitations=(),
        supporting_evidence=(
            f"evidence-{finding_id}",
        ),
        provenance=(
            (
                "finding_pipeline_version",
                "finding-v2",
            ),
        ),
    )


def build_evaluation() -> HypothesisEvaluation:
    return HypothesisEvaluation(
        id="hypothesis-evaluation-id",
        hypothesis_id="hypothesis-rsi",
        state=HypothesisEvaluationState.SUPPORTED,
        confidence=0.8,
        finding_refs=(
            "finding-a",
            "finding-b",
        ),
        rationale=(
            "supported",
        ),
        limitations=(),
        provenance=(
            (
                "evaluation_plan_version",
                "hypothesis-evaluation-v1",
            ),
        ),
    )


class StubFindingApplication(
    IndicatorComparativeFindingApplication
):
    def __init__(
        self,
        results: tuple[Finding, ...],
    ) -> None:
        self.results = results
        self.calls: list[
            dict[str, object]
        ] = []

    def run(
        self,
        **arguments: object,
    ) -> Finding:
        self.calls.append(dict(arguments))

        return self.results[
            len(self.calls) - 1
        ]


class StubHypothesisEvaluationApplication(
    HypothesisEvaluationApplication
):
    def __init__(
        self,
        result: HypothesisEvaluation,
    ) -> None:
        self.result = result
        self.calls: list[
            tuple[Finding, ...]
        ] = []

    def run(
        self,
        *,
        findings: tuple[Finding, ...],
    ) -> HypothesisEvaluation:
        self.calls.append(findings)

        return self.result


def build_application(
) -> tuple[
    IndicatorComparativeHypothesisEvaluationApplication,
    StubFindingApplication,
    StubHypothesisEvaluationApplication,
]:
    finding_application = StubFindingApplication(
        (
            build_finding("finding-a"),
            build_finding("finding-b"),
        )
    )
    evaluation_application = (
        StubHypothesisEvaluationApplication(
            build_evaluation()
        )
    )

    return (
        IndicatorComparativeHypothesisEvaluationApplication(
            finding_application=finding_application,
            hypothesis_evaluation_application=(
                evaluation_application
            ),
        ),
        finding_application,
        evaluation_application,
    )


def test_runs_requests_through_formal_evaluation(
) -> None:
    (
        application,
        finding_application,
        evaluation_application,
    ) = build_application()
    requests = (
        build_request(
            horizon=1,
            indicator_id="rsi",
        ),
        build_request(
            horizon=3,
            indicator_id="williams_r",
        ),
    )

    result = application.run(
        hypothesis_id=" hypothesis-rsi ",
        requests=requests,
        correlation_id="research-lifecycle-42",
    )

    assert result is evaluation_application.result
    assert len(finding_application.calls) == 2
    assert finding_application.calls[0][
        "hypothesis_id"
    ] == "hypothesis-rsi"
    assert finding_application.calls[0][
        "horizon"
    ] == 1
    assert finding_application.calls[1][
        "horizon"
    ] == 3
    assert finding_application.calls[1][
        "indicator_id"
    ] == "williams_r"
    assert finding_application.calls[0][
        "analysis_pipeline_version"
    ] == "finding-v2"
    assert finding_application.calls[0][
        "correlation_id"
    ] == "research-lifecycle-42"
    assert finding_application.calls[1][
        "correlation_id"
    ] == "research-lifecycle-42"
    assert evaluation_application.calls == [
        (
            finding_application.results[0],
            finding_application.results[1],
        )
    ]


@pytest.mark.parametrize(
    "invalid_dependency",
    (
        "finding_application",
        "hypothesis_evaluation_application",
    ),
)
def test_rejects_invalid_dependency(
    invalid_dependency: str,
) -> None:
    arguments: dict[str, object] = {
        "finding_application": (
            StubFindingApplication(
                (build_finding("finding-a"),)
            )
        ),
        "hypothesis_evaluation_application": (
            StubHypothesisEvaluationApplication(
                build_evaluation()
            )
        ),
    }
    arguments[invalid_dependency] = object()

    message = (
        "finding_application must be an "
        "IndicatorComparativeFindingApplication"
        if invalid_dependency
        == "finding_application"
        else (
            "hypothesis_evaluation_application "
            "must be a "
            "HypothesisEvaluationApplication"
        )
    )

    with pytest.raises(
        TypeError,
        match=message,
    ):
        IndicatorComparativeHypothesisEvaluationApplication(
            **arguments,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    ("requests", "error_type", "message"),
    (
        (
            [],
            TypeError,
            "requests must be a tuple",
        ),
        (
            (),
            ValueError,
            "requests must not be empty",
        ),
        (
            (object(),),
            TypeError,
            "each request must be an "
            "IndicatorComparativeFindingRequest",
        ),
    ),
)
def test_rejects_invalid_requests(
    requests: object,
    error_type: type[Exception],
    message: str,
) -> None:
    application, _, _ = build_application()

    with pytest.raises(
        error_type,
        match=message,
    ):
        application.run(
            hypothesis_id="hypothesis-rsi",
            requests=requests,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    ("hypothesis_id", "error_type", "message"),
    (
        (
            object(),
            TypeError,
            "hypothesis_id must be a string",
        ),
        (
            " ",
            ValueError,
            "hypothesis_id must not be empty",
        ),
    ),
)
def test_rejects_invalid_hypothesis_id(
    hypothesis_id: object,
    error_type: type[Exception],
    message: str,
) -> None:
    application, _, _ = build_application()

    with pytest.raises(
        error_type,
        match=message,
    ):
        application.run(
            hypothesis_id=hypothesis_id,  # type: ignore[arg-type]
            requests=(build_request(),),
        )


def test_request_requires_declared_horizon(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "horizon must be declared in "
            "outcome_specification"
        ),
    ):
        build_request(horizon=2)