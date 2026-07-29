from __future__ import annotations

from datetime import UTC, datetime

import pytest

from src.application.market_research_campaign_artifact_loader import (
    MarketResearchCampaignArtifactLoader,
)
from src.application.research_artifact_envelope import (
    ResearchArtifactEnvelopeFactory,
    ResearchArtifactSourceReference,
)
from src.research.campaign_design import CampaignDesign
from src.research.research_planner import (
    ResearchCampaignPlan,
    ResearchPlanner,
)


class FixedClock:
    def now(self) -> datetime:
        return datetime(
            2026,
            7,
            29,
            12,
            0,
            tzinfo=UTC,
        )


class FixedIdGenerator:
    def generate(self) -> str:
        return "artifact-campaign-loader"


def build_plan() -> ResearchCampaignPlan:
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
            ("source", "campaign-loader-test"),
        ),
    )

    return ResearchPlanner().plan(design)


def build_payload(
    plan: ResearchCampaignPlan,
) -> dict[str, object]:
    specification = (
        plan.experiment_specifications[0]
    )

    return {
        "campaign_design_id": (
            plan.campaign_design_id
        ),
        "campaign_plan_id": plan.id,
        "campaign_plan": plan.to_dict(),
        "experiment_count": 1,
        "experiments": [
            {
                "planned_experiment_id": (
                    specification.id
                ),
                "planned_specification": (
                    specification.to_dict()
                ),
                "artifact": {
                    "artifact_version": 1,
                    "specification": {
                        "symbol": (
                            specification.instrument
                        ),
                        "timeframe": (
                            specification.timeframe
                        ),
                    },
                    "cycle": {
                        "result": {
                            "id": (
                                "experiment-result-1"
                            ),
                            "experiment_id": (
                                "experiment-rsi"
                            ),
                            "success": True,
                        },
                    },
                },
            },
        ],
    }


def build_provenance(
    plan: ResearchCampaignPlan,
    *,
    experiment_count: int = 1,
) -> dict[str, object]:
    provenance: dict[str, object] = dict(
        plan.provenance
    )
    provenance.update(
        {
            "campaign_design_id": (
                plan.campaign_design_id
            ),
            "campaign_plan_fingerprint": (
                plan.fingerprint
            ),
            "campaign_plan_id": plan.id,
            "experiment_count": experiment_count,
            "question_id": plan.question_id,
        }
    )

    return provenance


def build_source_references(
    plan: ResearchCampaignPlan,
    *,
    result_id: str = "experiment-result-1",
) -> tuple[
    ResearchArtifactSourceReference,
    ...,
]:
    return (
        ResearchArtifactSourceReference(
            reference_type=(
                "research_campaign_plan"
            ),
            reference_id=plan.id,
            reference_fingerprint=(
                plan.fingerprint
            ),
        ),
        ResearchArtifactSourceReference(
            reference_type="experiment_result",
            reference_id=result_id,
        ),
    )


def build_serialized(
    *,
    plan: ResearchCampaignPlan | None = None,
    payload: dict[str, object] | None = None,
    artifact_type: str = (
        "market_research_campaign"
    ),
    provenance: dict[str, object] | None = None,
    source_references: tuple[
        ResearchArtifactSourceReference,
        ...,
    ] | None = None,
) -> dict[str, object]:
    actual_plan = plan or build_plan()
    actual_payload = (
        payload
        if payload is not None
        else build_payload(actual_plan)
    )
    actual_provenance = (
        provenance
        if provenance is not None
        else build_provenance(
            actual_plan,
            experiment_count=actual_payload[
                "experiment_count"
            ],
        )
    )
    actual_source_references = (
        source_references
        if source_references is not None
        else build_source_references(
            actual_plan
        )
    )
    factory = ResearchArtifactEnvelopeFactory(
        producer="campaign-loader-test",
        producer_version="git:test",
        clock=FixedClock(),
        id_generator=FixedIdGenerator(),
    )

    return factory.create(
        artifact_type=artifact_type,
        payload_schema_version=1,
        payload=actual_payload,
        provenance=actual_provenance,
        correlation_id="campaign-lifecycle-42",
        source_references=(
            actual_source_references
        ),
    ).to_dict()


def test_loads_complete_campaign_envelope(
) -> None:
    plan = build_plan()

    loaded = (
        MarketResearchCampaignArtifactLoader()
        .load(
            build_serialized(plan=plan)
        )
    )

    assert loaded.research_plan == plan
    assert len(loaded.experiments) == 1
    assert (
        loaded
        .experiments[0]
        .planned_specification
        == plan.experiment_specifications[0]
    )
    assert loaded.experiments[0].result_id == (
        "experiment-result-1"
    )
    assert loaded.experiments[0].artifact[
        "artifact_version"
    ] == 1
    assert loaded.envelope.correlation_id == (
        "campaign-lifecycle-42"
    )

    with pytest.raises(TypeError):
        loaded.experiments[0].artifact[
            "artifact_version"
        ] = 2


def test_rejects_non_mapping_artifact(
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "serialized artifact must be a mapping"
        ),
    ):
        (
            MarketResearchCampaignArtifactLoader()
            .load([])
        )


def test_rejects_other_artifact_type(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "artifact_type must be "
            "market_research_campaign"
        ),
    ):
        (
            MarketResearchCampaignArtifactLoader()
            .load(
                build_serialized(
                    artifact_type=(
                        "hypothesis_evaluation"
                    )
                )
            )
        )


def test_rejects_unknown_payload_field(
) -> None:
    plan = build_plan()
    payload = build_payload(plan)
    payload["unexpected"] = True

    with pytest.raises(
        ValueError,
        match="payload unknown fields: unexpected",
    ):
        (
            MarketResearchCampaignArtifactLoader()
            .load(
                build_serialized(
                    plan=plan,
                    payload=payload,
                )
            )
        )


def test_rejects_campaign_plan_id_mismatch(
) -> None:
    plan = build_plan()
    payload = build_payload(plan)
    campaign_plan = payload["campaign_plan"]

    assert isinstance(campaign_plan, dict)

    campaign_plan["id"] = (
        "research-campaign-plan:sha256:"
        + ("0" * 64)
    )

    with pytest.raises(
        ValueError,
        match=(
            "campaign_plan.id does not match "
            "campaign_plan fingerprint"
        ),
    ):
        (
            MarketResearchCampaignArtifactLoader()
            .load(
                build_serialized(
                    plan=plan,
                    payload=payload,
                )
            )
        )


def test_rejects_experiment_count_mismatch(
) -> None:
    plan = build_plan()
    payload = build_payload(plan)
    payload["experiment_count"] = 2

    with pytest.raises(
        ValueError,
        match=(
            "experiment_count does not match "
            "experiments"
        ),
    ):
        (
            MarketResearchCampaignArtifactLoader()
            .load(
                build_serialized(
                    plan=plan,
                    payload=payload,
                )
            )
        )


def test_rejects_experiment_outside_plan_order(
) -> None:
    plan = build_plan()
    payload = build_payload(plan)
    experiments = payload["experiments"]

    assert isinstance(experiments, list)
    assert isinstance(experiments[0], dict)

    experiments[0][
        "planned_experiment_id"
    ] = "campaign-experiment-specification:other"

    with pytest.raises(
        ValueError,
        match=(
            "planned_experiment_id does not "
            "match campaign_plan order"
        ),
    ):
        (
            MarketResearchCampaignArtifactLoader()
            .load(
                build_serialized(
                    plan=plan,
                    payload=payload,
                )
            )
        )


def test_rejects_mismatched_provenance(
) -> None:
    plan = build_plan()
    provenance = build_provenance(plan)
    provenance["question_id"] = "question-other"

    with pytest.raises(
        ValueError,
        match=(
            "provenance does not match "
            "campaign_plan"
        ),
    ):
        (
            MarketResearchCampaignArtifactLoader()
            .load(
                build_serialized(
                    plan=plan,
                    provenance=provenance,
                )
            )
        )


def test_rejects_mismatched_source_references(
) -> None:
    plan = build_plan()
    source_references = (
        ResearchArtifactSourceReference(
            reference_type=(
                "research_campaign_plan"
            ),
            reference_id=plan.id,
            reference_fingerprint=(
                plan.fingerprint
            ),
        ),
    )

    with pytest.raises(
        ValueError,
        match=(
            "source_references do not match "
            "campaign payload"
        ),
    ):
        (
            MarketResearchCampaignArtifactLoader()
            .load(
                build_serialized(
                    plan=plan,
                    source_references=(
                        source_references
                    ),
                )
            )
        )


def test_rejects_mismatched_result_reference(
) -> None:
    plan = build_plan()

    with pytest.raises(
        ValueError,
        match=(
            "source_references do not match "
            "campaign payload"
        ),
    ):
        (
            MarketResearchCampaignArtifactLoader()
            .load(
                build_serialized(
                    plan=plan,
                    source_references=(
                        build_source_references(
                            plan,
                            result_id=(
                                "experiment-result-other"
                            ),
                        )
                    ),
                )
            )
        )
