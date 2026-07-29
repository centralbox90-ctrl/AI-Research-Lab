from __future__ import annotations

from typing import Any

from src.application.research_artifact_serializer import (
    ResearchArtifactSerializer,
)
from src.application.run_market_research_campaign import (
    MarketResearchCampaignResult,
)


class MarketResearchCampaignArtifactPayloadFactory:
    """
    Creates the typed payload for one completed market campaign.
    """

    def __init__(
        self,
        artifact_serializer: (
            ResearchArtifactSerializer | None
        ) = None,
    ) -> None:
        if (
            artifact_serializer is not None
            and not isinstance(
                artifact_serializer,
                ResearchArtifactSerializer,
            )
        ):
            raise TypeError(
                "artifact_serializer must be a "
                "ResearchArtifactSerializer or None"
            )

        self._artifact_serializer = (
            artifact_serializer
            or ResearchArtifactSerializer()
        )

    def create(
        self,
        result: MarketResearchCampaignResult,
    ) -> dict[str, Any]:
        if not isinstance(
            result,
            MarketResearchCampaignResult,
        ):
            raise TypeError(
                "result must be a "
                "MarketResearchCampaignResult"
            )

        experiments = []

        for experiment_result in (
            result.experiment_results
        ):
            resolved_experiment = (
                experiment_result.resolved_experiment
            )
            planned_specification = (
                resolved_experiment
                .planned_specification
            )

            experiments.append(
                {
                    "planned_experiment_id": (
                        planned_specification.id
                    ),
                    "planned_specification": (
                        planned_specification.to_dict()
                    ),
                    "artifact": (
                        self._artifact_serializer.serialize(
                            resolved_experiment
                            .market_specification,
                            experiment_result.result,
                        )
                    ),
                }
            )

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
            "experiment_count": len(experiments),
            "experiments": experiments,
        }
