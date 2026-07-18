from typing import Any, Protocol


class SerializedResearchCampaignStore(Protocol):
    """
    Persistence boundary for serialized research campaigns.

    Implementations store application-safe dictionaries and do not
    reconstruct research domain objects.
    """

    def save(
        self,
        campaign_id: str,
        serialized_campaign: dict[str, Any],
    ) -> None:
        """
        Save serialized research-campaign data.
        """

    def get(
        self,
        campaign_id: str,
    ) -> dict[str, Any] | None:
        """
        Return serialized research-campaign data by campaign ID.
        """

    def list_campaign_ids(self) -> list[str]:
        """
        Return IDs of all stored research campaigns.
        """
