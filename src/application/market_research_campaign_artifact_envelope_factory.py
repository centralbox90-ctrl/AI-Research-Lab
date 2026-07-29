from __future__ import annotations

from src.application.market_research_campaign_artifact_payload_factory import (
    MarketResearchCampaignArtifactPayloadFactory,
)
from src.application.research_artifact_envelope import (
    ResearchArtifactEnvelope,
    ResearchArtifactEnvelopeFactory,
    ResearchArtifactSourceReference,
)
from src.application.run_market_research_campaign import (
    MarketResearchCampaignResult,
)


class MarketResearchCampaignArtifactEnvelopeFactory:
    """
    Creates envelopes for completed market research campaigns.
    """

    def __init__(
        self,
        *,
        envelope_factory: ResearchArtifactEnvelopeFactory,
        payload_factory: (
            MarketResearchCampaignArtifactPayloadFactory
            | None
        ) = None,
    ) -> None:
        if not isinstance(
            envelope_factory,
            ResearchArtifactEnvelopeFactory,
        ):
            raise TypeError(
                "envelope_factory must be a "
                "ResearchArtifactEnvelopeFactory"
            )

        if (
            payload_factory is not None
            and not isinstance(
                payload_factory,
                MarketResearchCampaignArtifactPayloadFactory,
            )
        ):
            raise TypeError(
                "payload_factory must be a "
                "MarketResearchCampaignArtifactPayloadFactory "
                "or None"
            )

        self._envelope_factory = envelope_factory
        self._payload_factory = (
            payload_factory
            or MarketResearchCampaignArtifactPayloadFactory()
        )

    def create(
        self,
        *,
        result: MarketResearchCampaignResult,
        correlation_id: str | None = None,
    ) -> ResearchArtifactEnvelope:
        if not isinstance(
            result,
            MarketResearchCampaignResult,
        ):
            raise TypeError(
                "result must be a "
                "MarketResearchCampaignResult"
            )

        plan = result.research_plan
        payload = self._payload_factory.create(
            result
        )
        source_references = [
            ResearchArtifactSourceReference(
                reference_type=(
                    "research_campaign_plan"
                ),
                reference_id=plan.id,
                reference_fingerprint=(
                    plan.fingerprint
                ),
            )
        ]

        for experiment_result in (
            result.experiment_results
        ):
            source_references.append(
                ResearchArtifactSourceReference(
                    reference_type=(
                        "experiment_result"
                    ),
                    reference_id=(
                        experiment_result
                        .result
                        .result
                        .id
                    ),
                )
            )

        provenance = dict(plan.provenance)
        provenance.update(
            {
                "campaign_design_id": (
                    plan.campaign_design_id
                ),
                "campaign_plan_fingerprint": (
                    plan.fingerprint
                ),
                "campaign_plan_id": plan.id,
                "experiment_count": len(
                    result.experiment_results
                ),
                "question_id": (
                    plan.question_id
                ),
            }
        )

        return self._envelope_factory.create(
            artifact_type=(
                "market_research_campaign"
            ),
            payload_schema_version=1,
            payload=payload,
            provenance=provenance,
            correlation_id=correlation_id,
            source_references=tuple(
                source_references
            ),
        )
