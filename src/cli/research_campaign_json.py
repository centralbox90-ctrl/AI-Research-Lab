import json
from typing import Any


class ResearchCampaignJsonPresenter:
    """
    Converts serialized research-campaign data into CLI-safe JSON text.

    The presenter accepts only application-safe dictionaries and does not
    depend on research domain models or repository implementations.
    """

    def render(
        self,
        serialized_campaign: dict[str, Any],
        *,
        indent: int | None = 2,
    ) -> str:
        return json.dumps(
            serialized_campaign,
            ensure_ascii=False,
            indent=indent,
            sort_keys=True,
        )