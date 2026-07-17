import json
from typing import Any


class ResearchCycleJsonPresenter:
    """
    Converts serialized research-cycle data into CLI-safe JSON text.

    The presenter accepts only application-safe dictionaries and does not
    depend on research domain models or repository implementations.
    """

    def render(
        self,
        serialized_cycle: dict[str, Any],
        *,
        indent: int | None = 2,
    ) -> str:
        return json.dumps(
            serialized_cycle,
            ensure_ascii=False,
            indent=indent,
            sort_keys=True,
        )