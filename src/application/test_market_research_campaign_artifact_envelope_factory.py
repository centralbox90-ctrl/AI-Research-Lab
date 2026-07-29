from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace

import pytest

from src.application.market_research_campaign_artifact_envelope_factory import (
    MarketResearchCampaignArtifactEnvelopeFactory,
)
from src.application.market_research_campaign_artifact_payload_factory import (
    MarketResearchCampaignArtifactPayloadFactory,
)
from src.application.research_artifact_envelope import (
    ResearchArtifactEnvelopeFactory,
)
from src.application.run_market_research_campaign import (
    MarketResearchCampaignResult,
)
from src.research.campaign_design import CampaignDesign
from src.research.experiment_result import (
    ExperimentResult,
)
from src.research.research_planner import (
    ResearchPlanner,
)


class FixedClock:
    def now(self) -> datetime:
        return datetime(
            2026,
            7,
            29,
            10,
            0,
            tzinfo=UTC,
        )


class FixedIdGenerator:
    def generate(self) -> str:
        return "artifact-campaign-envelope"


class StubPayloadFactory(
    MarketResearchCampaignArtifactPayloadFactory
):
    def __init__(self) -> None:
        self.results: list[
            MarketResearchCampaignResult
        ] = []

    def create(
        self,
        result: MarketResearchCampaignResult,
    ) -> dict[str, object]:
        self.results.append(result)

        return {
            "campaign_design_id": (
                result.research_plan.campaign_design_id
            ),
            "campaign_plan_id": (
                result.research_plan.id
            ),
            "campaign_plan": (
                result.research_plan.to_dict()
            ),
            "experiment_count": 1,
            "experiments": [
                {
                    "planned_experiment_id": (
                        result
                        .research_plan
                        .experiment_ids[0]
                    ),
                    "artifact": {
                        "artifact_version": 1,
                    },
                },
            ],
        }


def build_result(
) -> MarketResearchCampaignResult:
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
            ("source", "campaign-envelope-test"),
        ),
    )
    plan = ResearchPlanner().plan(design)
    result = object.__new__(
        MarketResearchCampaignResult
    )
    object.__setattr__(
        result,
        "resolved_plan",
        SimpleNamespace(
            research_plan=plan,
        ),
    )
    object.__setattr__(
        result,
        "experiment_results",
        (
            SimpleNamespace(
                result=SimpleNamespace(
                    result=ExperimentResult(
                        id="experiment-result-1",
                        experiment_id=(
                            "experiment-rsi"
                        ),
                        success=True,
                    ),
                ),
            ),
        ),
    )

    return result


def build_factory(
    payload_factory: (
        MarketResearchCampaignArtifactPayloadFactory
        | None
    ) = None,
) -> MarketResearchCampaignArtifactEnvelopeFactory:
    return (
        MarketResearchCampaignArtifactEnvelopeFactory(
            envelope_factory=(
                ResearchArtifactEnvelopeFactory(
                    producer=(
                        "market-campaign-test"
                    ),
                    producer_version="git:test",
                    clock=FixedClock(),
                    id_generator=FixedIdGenerator(),
                )
            ),
            payload_factory=payload_factory,
        )
    )


def test_creates_campaign_envelope(
) -> None:
    result = build_result()
    payload_factory = StubPayloadFactory()

    envelope = build_factory(
        payload_factory
    ).create(
        result=result,
        correlation_id=" campaign-lifecycle-42 ",
    )
    serialized = envelope.to_dict()
    plan = result.research_plan

    assert payload_factory.results == [
        result,
    ]
    assert serialized["schema_version"] == 1
    assert serialized["artifact_type"] == (
        "market_research_campaign"
    )
    assert serialized[
        "payload_schema_version"
    ] == 1
    assert serialized["artifact_id"] == (
        "artifact-campaign-envelope"
    )
    assert serialized["producer"] == (
        "market-campaign-test"
    )
    assert serialized["producer_version"] == (
        "git:test"
    )
    assert serialized["correlation_id"] == (
        "campaign-lifecycle-42"
    )
    assert serialized["payload"][
        "campaign_plan_id"
    ] == plan.id
    assert serialized["payload"][
        "experiment_count"
    ] == 1
    assert len(
        serialized["payload_fingerprint"]
    ) == 64
    assert serialized["provenance"][
        "campaign_design_id"
    ] == plan.campaign_design_id
    assert serialized["provenance"][
        "campaign_plan_fingerprint"
    ] == plan.fingerprint
    assert serialized["provenance"][
        "experiment_count"
    ] == 1
    assert serialized["source_references"] == [
        {
            "reference_type": (
                "research_campaign_plan"
            ),
            "reference_id": plan.id,
            "reference_version": None,
            "reference_fingerprint": (
                plan.fingerprint
            ),
        },
        {
            "reference_type": (
                "experiment_result"
            ),
            "reference_id": (
                "experiment-result-1"
            ),
            "reference_version": None,
            "reference_fingerprint": None,
        },
    ]


def test_rejects_invalid_campaign_result(
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "result must be a "
            "MarketResearchCampaignResult"
        ),
    ):
        build_factory(
            StubPayloadFactory()
        ).create(
            result=object(),
        )


def test_rejects_invalid_envelope_factory(
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "envelope_factory must be a "
            "ResearchArtifactEnvelopeFactory"
        ),
    ):
        MarketResearchCampaignArtifactEnvelopeFactory(
            envelope_factory=object(),
        )


def test_rejects_invalid_payload_factory(
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "payload_factory must be a "
            "MarketResearchCampaignArtifactPayloadFactory "
            "or None"
        ),
    ):
        MarketResearchCampaignArtifactEnvelopeFactory(
            envelope_factory=(
                ResearchArtifactEnvelopeFactory(
                    producer="test",
                    producer_version="git:test",
                )
            ),
            payload_factory=object(),
        )
