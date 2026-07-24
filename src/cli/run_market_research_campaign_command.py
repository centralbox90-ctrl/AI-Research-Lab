from __future__ import annotations

import json
from pathlib import Path

from src.application.campaign_design_loader import (
    CampaignDesignLoader,
)
from src.application.market_experiment_registration_loader import (
    MarketExperimentRegistrationLoader,
)
from src.application.research_campaign_plan_market_adapter import (
    ResearchCampaignPlanMarketAdapter,
)
from src.application.run_market_research_campaign import (
    MarketResearchExperimentRunner,
    RunMarketResearchCampaign,
)
from src.cli.market_research_campaign_presenter import (
    MarketResearchCampaignPresenter,
)
from src.research.research_planner import (
    ResearchPlanner,
)


class RunMarketResearchCampaignCommand:
    """
    Runs a campaign from design and registration JSON files.
    """

    def __init__(
        self,
        *,
        runner: MarketResearchExperimentRunner,
        planner: ResearchPlanner | None = None,
        design_loader: CampaignDesignLoader | None = None,
        registration_loader: (
            MarketExperimentRegistrationLoader | None
        ) = None,
        presenter: (
            MarketResearchCampaignPresenter | None
        ) = None,
    ) -> None:
        if not callable(
            getattr(runner, "execute", None)
        ):
            raise TypeError(
                "runner must provide a callable execute method"
            )

        if (
            planner is not None
            and not isinstance(
                planner,
                ResearchPlanner,
            )
        ):
            raise TypeError(
                "planner must be a ResearchPlanner or None"
            )

        if (
            design_loader is not None
            and not isinstance(
                design_loader,
                CampaignDesignLoader,
            )
        ):
            raise TypeError(
                "design_loader must be a "
                "CampaignDesignLoader or None"
            )

        if (
            registration_loader is not None
            and not isinstance(
                registration_loader,
                MarketExperimentRegistrationLoader,
            )
        ):
            raise TypeError(
                "registration_loader must be a "
                "MarketExperimentRegistrationLoader or None"
            )

        if (
            presenter is not None
            and not isinstance(
                presenter,
                MarketResearchCampaignPresenter,
            )
        ):
            raise TypeError(
                "presenter must be a "
                "MarketResearchCampaignPresenter or None"
            )

        self._runner = runner
        self._planner = planner or ResearchPlanner()
        self._design_loader = (
            design_loader
            or CampaignDesignLoader()
        )
        self._registration_loader = (
            registration_loader
            or MarketExperimentRegistrationLoader()
        )
        self._presenter = (
            presenter
            or MarketResearchCampaignPresenter()
        )

    def execute(
        self,
        design_path: str | Path,
        registration_path: str | Path,
        *,
        indent: int | None = 2,
    ) -> str:
        design = self._design_loader.load(
            design_path
        )
        plan = self._planner.plan(design)
        resolver = self._registration_loader.load(
            registration_path,
            plan=plan,
        )
        application = RunMarketResearchCampaign(
            planner=self._planner,
            adapter=ResearchCampaignPlanMarketAdapter(
                resolver
            ),
            runner=self._runner,
        )
        result = application.execute(design)
        payload = self._presenter.present(result)

        return json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            indent=indent,
        )
