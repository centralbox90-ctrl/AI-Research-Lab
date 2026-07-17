import json
from pathlib import Path

from src.application.market_experiment_specification_loader import (
    MarketExperimentSpecificationLoader,
)
from src.application.run_market_research import (
    RunMarketResearch,
)
from src.application.research_cycle_serializer import (
    ResearchCycleSerializer,
)


class RunMarketResearchCommand:
    """
    CLI command for executing one market research specification.

    The command coordinates:
    JSON specification loading,
    application execution,
    and JSON rendering.

    It does not contain research logic or market execution logic.
    """

    def __init__(
        self,
        run_market_research: RunMarketResearch,
        loader: (
            MarketExperimentSpecificationLoader | None
        ) = None,
        serializer: (
            ResearchCycleSerializer | None
        ) = None,
    ) -> None:

        self.run_market_research = run_market_research

        self.loader = (
            loader
            or MarketExperimentSpecificationLoader()
        )

        self.serializer = (
            serializer
            or ResearchCycleSerializer()
        )

    def execute(
        self,
        specification_path: str | Path,
        *,
        indent: int | None = 2,
    ) -> str:
        """
        Execute research from JSON specification.

        Returns serialized research-cycle JSON.
        """

        specification = self.loader.load(
            specification_path,
        )

        cycle = self.run_market_research.execute(
            specification,
        )

        serialized = self.serializer.serialize(
            cycle,
        )

        return json.dumps(
            serialized,
            ensure_ascii=False,
            indent=indent,
        )