from __future__ import annotations

from typing import Any

from src.application.market_research_campaign_artifact_payload_factory import (
    MarketResearchCampaignArtifactPayloadFactory,
)
from src.application.market_research_campaign_artifact_payload_factory import (
    MarketResearchCampaignArtifactPayloadFactory,
)
from src.application.research_artifact_serializer import (
    ResearchArtifactSerializer,
)
from src.application.run_market_research_campaign import (
    MarketResearchCampaignResult,
)


class MarketResearchCampaignPresenter:
    """
    Presents one completed campaign as a versioned artifact.
    """

    ARTIFACT_VERSION = 1

    def __init__(
        self,
        artifact_serializer: (
            ResearchArtifactSerializer | None
        ) = None,
    ) -> None:
        self._payload_factory = (
            MarketResearchCampaignArtifactPayloadFactory(
                artifact_serializer=(
                    artifact_serializer
                )
            )
        )

    def present(
        self,
        result: MarketResearchCampaignResult,
    ) -> dict[str, Any]:
        payload = self._payload_factory.create(
            result
        )

        return {
            "artifact_type": (
                "market_research_campaign"
            ),
            "artifact_version": (
                self.ARTIFACT_VERSION
            ),
            **payload,
        }
