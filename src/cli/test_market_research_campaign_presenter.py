import json
from datetime import datetime, timezone

import pytest

from src.application.in_memory_market_experiment_specification_resolver import (
    InMemoryMarketExperimentSpecificationResolver,
)
from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
    MarketPositionDirection,
)
from src.application.research_artifact_serializer import (
    ResearchArtifactSerializer,
)
from src.application.research_campaign_plan_market_adapter import (
    ResearchCampaignPlanMarketAdapter,
)
from src.application.run_market_research_campaign import (
    MarketResearchCampaignExperimentResult,
    MarketResearchCampaignResult,
)
from src.cli.market_research_campaign_presenter import (
    MarketResearchCampaignPresenter,
)
from src.research.campaign_design import CampaignDesign
from src.research.cycle_results import (
    NextExperimentResearchCycleResult,
)
from src.research.research_planner import (
    CampaignExperimentSpecification,
    ResearchPlanner,
)


class StubArtifactSerializer(
    ResearchArtifactSerializer
):
    def __init__(self) -> None:
        self.calls: list[
            tuple[
                MarketExperimentSpecification,
                NextExperimentResearchCycleResult,
            ]
        ] = []

    def serialize(
        self,
        specification: MarketExperimentSpecification,
        cycle: NextExperimentResearchCycleResult,
        metadata=None,
        lineage=None,
        comparisons=None,
        research_environment=None,
    ) -> dict[str, object]:
        self.calls.append(
            (
                specification,
                cycle,
            )
        )

        return {
            "artifact_version": 1,
            "specification": {
                "symbol": specification.symbol,
                "timeframe": specification.timeframe,
            },
            "cycle": {
                "result_type": (
                    type(cycle).__name__
                ),
            },
        }


def build_market_specification(
    planned_specification: CampaignExperimentSpecification,
) -> MarketExperimentSpecification:
    return MarketExperimentSpecification(
        executor_type="market_backtest",
        question_title=(
            "Does RSI oversold predict positive returns?"
        ),
        question_description=(
            "Evaluate an RSI signal on historical data."
        ),
        hypothesis_title=(
            "RSI oversold values precede positive returns"
        ),
        hypothesis_description=(
            "The registered RSI signal should "
            "produce positive returns."
        ),
        expected_result="Positive net profit.",
        experiment_title=(
            f"{planned_specification.instrument} "
            f"{planned_specification.timeframe} backtest"
        ),
        experiment_description=(
            "Execute one campaign experiment."
        ),
        data_source="historical_csv",
        symbol=planned_specification.instrument,
        timeframe=planned_specification.timeframe,
        start_at=datetime(
            2024,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        end_at=datetime(
            2024,
            12,
            31,
            tzinfo=timezone.utc,
        ),
        entry_rule="rsi-entry-v1",
        exit_rule="risk-exit-v1",
        direction=MarketPositionDirection.LONG,
        stop_loss_percent=1.0,
        take_profit_percent=2.0,
        max_holding_bars=24,
    )


def build_result(
) -> tuple[
    MarketResearchCampaignResult,
    tuple[
        NextExperimentResearchCycleResult,
        ...,
    ],
]:
    design = CampaignDesign(
        question_id="question-rsi",
        hypothesis_ids=("hypothesis-rsi",),
        instruments=(
            "BTCUSDT",
            "EURUSD",
        ),
        timeframes=("H1",),
        data_periods=("training-period-v1",),
        indicator_configurations=("rsi-period-14",),
        signal_rules=("rsi-entry-v1",),
        execution_policies=("risk-policy-v1",),
        baselines=("unconditional-v1",),
        validation_strategy="walk-forward-v1",
        evaluation_plan_ref="comparison-v1",
        provenance=(
            ("source", "presenter-test"),
        ),
    )
    plan = ResearchPlanner().plan(design)
    registrations = {
        planned_specification.id: (
            build_market_specification(
                planned_specification
            )
        )
        for planned_specification
        in plan.experiment_specifications
    }
    resolved_plan = ResearchCampaignPlanMarketAdapter(
        InMemoryMarketExperimentSpecificationResolver(
            registrations
        )
    ).adapt(plan)
    cycles = tuple(
        object.__new__(
            NextExperimentResearchCycleResult
        )
        for _ in resolved_plan.experiments
    )
    experiment_results = tuple(
        MarketResearchCampaignExperimentResult(
            resolved_experiment=resolved_experiment,
            result=cycle,
        )
        for resolved_experiment, cycle in zip(
            resolved_plan.experiments,
            cycles,
            strict=True,
        )
    )

    return (
        MarketResearchCampaignResult(
            resolved_plan=resolved_plan,
            experiment_results=experiment_results,
        ),
        cycles,
    )


def test_presents_versioned_campaign_artifact() -> None:
    result, cycles = build_result()
    serializer = StubArtifactSerializer()

    payload = MarketResearchCampaignPresenter(
        artifact_serializer=serializer
    ).present(result)

    assert payload["artifact_type"] == (
        "market_research_campaign"
    )
    assert payload["artifact_version"] == 1
    assert payload["campaign_design_id"] == (
        result.research_plan.campaign_design_id
    )
    assert payload["campaign_plan_id"] == (
        result.research_plan.id
    )
    assert payload["experiment_count"] == 2
    assert payload["campaign_plan"] == (
        result.research_plan.to_dict()
    )
    serialized_cycles = tuple(
        cycle
        for _, cycle in serializer.calls
    )
    assert len(serialized_cycles) == len(cycles)
    assert all(
        actual is expected
        for actual, expected in zip(
            serialized_cycles,
            cycles,
            strict=True,
        )
    )


def test_preserves_planned_experiment_order() -> None:
    result, _ = build_result()

    payload = MarketResearchCampaignPresenter(
        artifact_serializer=StubArtifactSerializer()
    ).present(result)

    assert tuple(
        experiment["planned_experiment_id"]
        for experiment in payload["experiments"]
    ) == result.research_plan.experiment_ids

    assert tuple(
        experiment["planned_specification"]["id"]
        for experiment in payload["experiments"]
    ) == result.research_plan.experiment_ids


def test_includes_each_market_artifact() -> None:
    result, _ = build_result()

    payload = MarketResearchCampaignPresenter(
        artifact_serializer=StubArtifactSerializer()
    ).present(result)

    assert tuple(
        (
            experiment["artifact"]
            ["specification"]["symbol"]
        )
        for experiment in payload["experiments"]
    ) == tuple(
        specification.symbol
        for specification
        in result.resolved_plan.market_specifications
    )


def test_presented_payload_is_json_compatible() -> None:
    result, _ = build_result()

    payload = MarketResearchCampaignPresenter(
        artifact_serializer=StubArtifactSerializer()
    ).present(result)

    rendered = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
    )

    assert (
        json.loads(rendered)["campaign_plan_id"]
        == result.research_plan.id
    )


def test_rejects_invalid_result() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "result must be a "
            "MarketResearchCampaignResult"
        ),
    ):
        MarketResearchCampaignPresenter(
            artifact_serializer=(
                StubArtifactSerializer()
            )
        ).present(object())


def test_rejects_invalid_artifact_serializer() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "artifact_serializer must be a "
            "ResearchArtifactSerializer or None"
        ),
    ):
        MarketResearchCampaignPresenter(
            artifact_serializer=object()
        )
