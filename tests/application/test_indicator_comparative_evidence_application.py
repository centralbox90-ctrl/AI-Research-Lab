from datetime import UTC, datetime

import pytest

from src.application import MarketPositionDirection
from src.application.indicator_comparative_evidence_application import (
    IndicatorComparativeEvidenceApplication,
)
from src.application.indicator_comparative_evidence_service import (
    IndicatorComparativeEvidenceService,
)
from src.application.indicator_comparative_research_application import (
    IndicatorComparativeResearchApplication,
)
from src.application.indicator_comparative_research_result import (
    IndicatorComparativeResearchResult,
)
from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
)
from src.research.evidence import (
    Evidence,
    EvidenceDirection,
    EvidenceStrength,
)
from src.research.outcome_specification import (
    ForwardReturnSpecification,
)


def build_market_specification(
    *,
    start_at: datetime,
    end_at: datetime,
    **overrides: object,
) -> MarketExperimentSpecification:
    arguments: dict[str, object] = {
        "executor_type": "market_backtest",
        "question_title": (
            "Does RSI predict forward returns?"
        ),
        "question_description": (
            "Compare RSI observations with the "
            "market baseline."
        ),
        "hypothesis_title": (
            "RSI observations precede positive returns"
        ),
        "hypothesis_description": (
            "RSI observations are expected to produce "
            "positive forward return differences."
        ),
        "expected_result": (
            "Replicated positive return differences."
        ),
        "experiment_title": (
            "RSI comparative research"
        ),
        "experiment_description": (
            "Run comparative RSI research on one "
            "independent market period."
        ),
        "data_source": "mt5",
        "symbol": "EURUSD",
        "timeframe": "H1",
        "start_at": start_at,
        "end_at": end_at,
        "entry_rule": "rsi_observation",
        "exit_rule": "forward_return",
        "direction": MarketPositionDirection.LONG,
        "stop_loss_percent": 1.0,
        "take_profit_percent": 2.0,
        "max_holding_bars": 10,
        "commission_percent": 0.0,
        "slippage_percent": 0.0,
        "research_specification": None,
        "strategy_parameters": {},
        "tags": (
            "rsi",
            "comparative",
        ),
    }
    arguments.update(overrides)

    return MarketExperimentSpecification(
        **arguments,  # type: ignore[arg-type]
    )


def build_specifications(
) -> tuple[
    MarketExperimentSpecification,
    MarketExperimentSpecification,
]:
    return (
        build_market_specification(
            start_at=datetime(
                2025,
                7,
                1,
                tzinfo=UTC,
            ),
            end_at=datetime(
                2026,
                1,
                1,
                tzinfo=UTC,
            ),
        ),
        build_market_specification(
            start_at=datetime(
                2026,
                1,
                1,
                tzinfo=UTC,
            ),
            end_at=datetime(
                2026,
                7,
                1,
                tzinfo=UTC,
            ),
        ),
    )


def build_evidence() -> Evidence:
    return Evidence(
        id="evidence-id",
        hypothesis_id="hypothesis-rsi",
        observation_refs=(
            "dataset-a:horizon:3",
            "dataset-b:horizon:3",
        ),
        direction=(
            EvidenceDirection.INCONCLUSIVE
        ),
        strength=EvidenceStrength.WEAK,
        confidence=0.475,
        consistency=1.0,
        robustness=1.0,
        provenance=(
            (
                "research_fingerprint",
                "research-id",
            ),
        ),
    )


class RecordingResearchApplication(
    IndicatorComparativeResearchApplication
):
    def __init__(
        self,
        results: tuple[
            IndicatorComparativeResearchResult,
            ...,
        ],
    ) -> None:
        self.results = results
        self.calls: list[
            dict[str, object]
        ] = []

    def run(
        self,
        *,
        market_specification: MarketExperimentSpecification,
        indicator_id: str,
        outcome_specification: ForwardReturnSpecification,
    ) -> IndicatorComparativeResearchResult:
        result_index = len(self.calls)
        self.calls.append(
            {
                "market_specification": (
                    market_specification
                ),
                "indicator_id": indicator_id,
                "outcome_specification": (
                    outcome_specification
                ),
            }
        )

        return self.results[result_index]


class RecordingEvidenceService(
    IndicatorComparativeEvidenceService
):
    def __init__(
        self,
        evidence: Evidence,
    ) -> None:
        self.evidence = evidence
        self.calls: list[
            dict[str, object]
        ] = []

    def evaluate(
        self,
        *,
        hypothesis_id: str,
        results: tuple[
            IndicatorComparativeResearchResult,
            ...,
        ],
        horizon: int,
    ) -> Evidence:
        self.calls.append(
            {
                "hypothesis_id": hypothesis_id,
                "results": results,
                "horizon": horizon,
            }
        )

        return self.evidence


def build_application(
) -> tuple[
    IndicatorComparativeEvidenceApplication,
    RecordingResearchApplication,
    RecordingEvidenceService,
    tuple[
        IndicatorComparativeResearchResult,
        IndicatorComparativeResearchResult,
    ],
    Evidence,
]:
    results = (
        object.__new__(
            IndicatorComparativeResearchResult
        ),
        object.__new__(
            IndicatorComparativeResearchResult
        ),
    )
    evidence = build_evidence()
    research_application = (
        RecordingResearchApplication(results)
    )
    evidence_service = (
        RecordingEvidenceService(evidence)
    )
    application = (
        IndicatorComparativeEvidenceApplication(
            research_application=(
                research_application
            ),
            evidence_service=evidence_service,
        )
    )

    return (
        application,
        research_application,
        evidence_service,
        results,
        evidence,
    )


def test_runs_research_for_each_independent_period(
) -> None:
    (
        application,
        research_application,
        evidence_service,
        results,
        expected_evidence,
    ) = build_application()
    specifications = build_specifications()
    outcome_specification = (
        ForwardReturnSpecification(
            horizons=(1, 3, 5),
        )
    )

    evidence = application.run(
        hypothesis_id="  hypothesis-rsi  ",
        market_specifications=specifications,
        indicator_id="  rsi  ",
        outcome_specification=(
            outcome_specification
        ),
        horizon=3,
    )

    assert evidence is expected_evidence
    assert len(research_application.calls) == 2
    assert (
        research_application.calls[0][
            "market_specification"
        ]
        is specifications[0]
    )
    assert (
        research_application.calls[1][
            "market_specification"
        ]
        is specifications[1]
    )

    for call in research_application.calls:
        assert call["indicator_id"] == "rsi"
        assert (
            call["outcome_specification"]
            is outcome_specification
        )

    assert evidence_service.calls == [
        {
            "hypothesis_id": "hypothesis-rsi",
            "results": results,
            "horizon": 3,
        }
    ]


@pytest.mark.parametrize(
    (
        "field_name",
        "invalid_value",
        "message",
    ),
    (
        (
            "research_application",
            object(),
            "research_application must be an "
            "IndicatorComparativeResearchApplication",
        ),
        (
            "evidence_service",
            object(),
            "evidence_service must be an "
            "IndicatorComparativeEvidenceService",
        ),
    ),
)
def test_rejects_invalid_dependencies(
    field_name: str,
    invalid_value: object,
    message: str,
) -> None:
    (
        _,
        research_application,
        evidence_service,
        _,
        _,
    ) = build_application()
    arguments: dict[str, object] = {
        "research_application": (
            research_application
        ),
        "evidence_service": evidence_service,
    }
    arguments[field_name] = invalid_value

    with pytest.raises(
        TypeError,
        match=message,
    ):
        IndicatorComparativeEvidenceApplication(
            **arguments,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    (
        "field_name",
        "invalid_value",
        "error_type",
        "message",
    ),
    (
        (
            "hypothesis_id",
            None,
            TypeError,
            "hypothesis_id must be a string",
        ),
        (
            "hypothesis_id",
            "   ",
            ValueError,
            "hypothesis_id must not be empty",
        ),
        (
            "indicator_id",
            None,
            TypeError,
            "indicator_id must be a string",
        ),
        (
            "indicator_id",
            "   ",
            ValueError,
            "indicator_id must not be empty",
        ),
    ),
)
def test_rejects_invalid_identity_before_research(
    field_name: str,
    invalid_value: object,
    error_type: type[Exception],
    message: str,
) -> None:
    (
        application,
        research_application,
        _,
        _,
        _,
    ) = build_application()
    arguments: dict[str, object] = {
        "hypothesis_id": "hypothesis-rsi",
        "market_specifications": (
            build_specifications()
        ),
        "indicator_id": "rsi",
        "outcome_specification": (
            ForwardReturnSpecification(
                horizons=(1, 3, 5),
            )
        ),
        "horizon": 3,
    }
    arguments[field_name] = invalid_value

    with pytest.raises(
        error_type,
        match=message,
    ):
        application.run(
            **arguments,  # type: ignore[arg-type]
        )

    assert research_application.calls == []


def test_rejects_invalid_outcome_before_research(
) -> None:
    (
        application,
        research_application,
        _,
        _,
        _,
    ) = build_application()

    with pytest.raises(
        TypeError,
        match=(
            "outcome_specification must be a "
            "ForwardReturnSpecification"
        ),
    ):
        application.run(
            hypothesis_id="hypothesis-rsi",
            market_specifications=(
                build_specifications()
            ),
            indicator_id="rsi",
            outcome_specification=object(),
            horizon=3,
        )

    assert research_application.calls == []


@pytest.mark.parametrize(
    (
        "horizon",
        "error_type",
        "message",
    ),
    (
        (
            True,
            TypeError,
            "horizon must be an integer",
        ),
        (
            0,
            ValueError,
            "horizon must be positive",
        ),
        (
            2,
            ValueError,
            "horizon must be included in "
            "outcome_specification",
        ),
    ),
)
def test_rejects_invalid_horizon_before_research(
    horizon: object,
    error_type: type[Exception],
    message: str,
) -> None:
    (
        application,
        research_application,
        _,
        _,
        _,
    ) = build_application()

    with pytest.raises(
        error_type,
        match=message,
    ):
        application.run(
            hypothesis_id="hypothesis-rsi",
            market_specifications=(
                build_specifications()
            ),
            indicator_id="rsi",
            outcome_specification=(
                ForwardReturnSpecification(
                    horizons=(1, 3, 5),
                )
            ),
            horizon=horizon,
        )

    assert research_application.calls == []


@pytest.mark.parametrize(
    (
        "specifications",
        "error_type",
        "message",
    ),
    (
        (
            [],
            TypeError,
            "market_specifications must be a tuple",
        ),
        (
            (),
            ValueError,
            "market_specifications must not be empty",
        ),
        (
            (object(),),
            TypeError,
            "each market specification must be a "
            "MarketExperimentSpecification",
        ),
    ),
)
def test_rejects_invalid_market_specifications(
    specifications: object,
    error_type: type[Exception],
    message: str,
) -> None:
    (
        application,
        research_application,
        _,
        _,
        _,
    ) = build_application()

    with pytest.raises(
        error_type,
        match=message,
    ):
        application.run(
            hypothesis_id="hypothesis-rsi",
            market_specifications=specifications,
            indicator_id="rsi",
            outcome_specification=(
                ForwardReturnSpecification(
                    horizons=(1, 3, 5),
                )
            ),
            horizon=3,
        )

    assert research_application.calls == []


@pytest.mark.parametrize(
    (
        "field_name",
        "invalid_value",
        "message",
    ),
    (
        (
            "symbol",
            "GBPUSD",
            "market specifications must use "
            "the same symbol",
        ),
        (
            "timeframe",
            "M15",
            "market specifications must use "
            "the same timeframe",
        ),
    ),
)
def test_rejects_incompatible_markets_before_research(
    field_name: str,
    invalid_value: object,
    message: str,
) -> None:
    (
        application,
        research_application,
        _,
        _,
        _,
    ) = build_application()
    first, _ = build_specifications()
    second = build_market_specification(
        start_at=datetime(
            2026,
            1,
            1,
            tzinfo=UTC,
        ),
        end_at=datetime(
            2026,
            7,
            1,
            tzinfo=UTC,
        ),
        **{field_name: invalid_value},
    )

    with pytest.raises(
        ValueError,
        match=message,
    ):
        application.run(
            hypothesis_id="hypothesis-rsi",
            market_specifications=(
                first,
                second,
            ),
            indicator_id="rsi",
            outcome_specification=(
                ForwardReturnSpecification(
                    horizons=(1, 3, 5),
                )
            ),
            horizon=3,
        )

    assert research_application.calls == []
