from __future__ import annotations

from datetime import datetime, timezone

import pytest

from src.application.in_memory_market_experiment_specification_resolver import (
    InMemoryMarketExperimentSpecificationResolver,
)
from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
    MarketPositionDirection,
)
from src.application.market_research_campaign_artifact_payload_factory import (
    MarketResearchCampaignArtifactPayloadFactory,
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
            "Does RSI predict positive returns?"
        ),
        question_description=(
            "Evaluate one registered market."
        ),
        hypothesis_title=(
            "RSI precedes positive returns"
        ),
        hypothesis_description=(
            "The signal should produce "
            "positive returns."
        ),
        expected_result="Positive net profit.",
        experiment_title="EURUSD H1 RSI backtest",
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
    MarketExperimentSpecification,
    NextExperimentResearchCycleResult,
]:
    design = CampaignDesign(
        question_id="question-rsi",
        hypothesis_ids=("hypothesis-rsi",),
        instruments=("EURUSD",),
        timeframes=("H1",),
        data_periods=("training-period-v1",),
        indicator_configurations=(
            "rsi-period-14",
        ),
        signal_rules=("rsi-entry-v1",),
        execution_policies=("risk-policy-v1",),
        baselines=("unconditional-v1",),
        validation_strategy="walk-forward-v1",
        evaluation_plan_ref="comparison-v1",
        provenance=(
            ("source", "payload-factory-test"),
        ),
    )
    plan = ResearchPlanner().plan(design)
    planned_specification = (
        plan.experiment_specifications[0]
    )
    market_specification = (
        build_market_specification(
            planned_specification
        )
    )
    resolved_plan = (
        ResearchCampaignPlanMarketAdapter(
            InMemoryMarketExperimentSpecificationResolver(
                {
                    planned_specification.id: (
                        market_specification
                    ),
                }
            )
        ).adapt(plan)
    )
    cycle = object.__new__(
        NextExperimentResearchCycleResult
    )
    result = MarketResearchCampaignResult(
        resolved_plan=resolved_plan,
        experiment_results=(
            MarketResearchCampaignExperimentResult(
                resolved_experiment=(
                    resolved_plan.experiments[0]
                ),
                result=cycle,
            ),
        ),
    )

    return (
        result,
        market_specification,
        cycle,
    )


def test_creates_complete_campaign_payload(
) -> None:
    result, specification, cycle = (
        build_result()
    )
    serializer = StubArtifactSerializer()

    payload = (
        MarketResearchCampaignArtifactPayloadFactory(
            artifact_serializer=serializer
        ).create(result)
    )

    assert payload["campaign_design_id"] == (
        result.research_plan.campaign_design_id
    )
    assert payload["campaign_plan_id"] == (
        result.research_plan.id
    )
    assert payload["campaign_plan"] == (
        result.research_plan.to_dict()
    )
    assert payload["experiment_count"] == 1
    assert len(payload["experiments"]) == 1

    experiment = payload["experiments"][0]

    assert experiment[
        "planned_experiment_id"
    ] == result.research_plan.experiment_ids[0]
    assert experiment[
        "planned_specification"
    ]["id"] == (
        result.research_plan.experiment_ids[0]
    )
    assert experiment["artifact"][
        "specification"
    ]["symbol"] == "EURUSD"
    assert len(serializer.calls) == 1
    assert serializer.calls[0][0] is (
        specification
    )
    assert serializer.calls[0][1] is cycle


def test_rejects_invalid_campaign_result(
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "result must be a "
            "MarketResearchCampaignResult"
        ),
    ):
        (
            MarketResearchCampaignArtifactPayloadFactory()
            .create(object())
        )


def test_rejects_invalid_artifact_serializer(
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "artifact_serializer must be a "
            "ResearchArtifactSerializer or None"
        ),
    ):
        MarketResearchCampaignArtifactPayloadFactory(
            artifact_serializer=object()
        )
