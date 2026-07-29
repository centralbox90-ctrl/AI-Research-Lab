from __future__ import annotations

import json
from pathlib import Path

from src.application.campaign_design_loader import (
    CampaignDesignLoader,
)
from src.application.market_experiment_registration_loader import (
    MarketExperimentRegistrationLoader,
)
from src.application.market_research_campaign_artifact_envelope_factory import (
    MarketResearchCampaignArtifactEnvelopeFactory,
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
        artifact_envelope_factory: (
            MarketResearchCampaignArtifactEnvelopeFactory
            | None
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

        if (
            artifact_envelope_factory is not None
            and not isinstance(
                artifact_envelope_factory,
                MarketResearchCampaignArtifactEnvelopeFactory,
            )
        ):
            raise TypeError(
                "artifact_envelope_factory must be a "
                "MarketResearchCampaignArtifactEnvelopeFactory "
                "or None"
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
        self._artifact_envelope_factory = (
            artifact_envelope_factory
        )

    def execute(
        self,
        design_path: str | Path,
        registration_path: str | Path,
        *,
        indent: int | None = 2,
        correlation_id: str | None = None,
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

        if self._artifact_envelope_factory is not None:
            payload = (
                self._artifact_envelope_factory.create(
                    result=result,
                    correlation_id=correlation_id,
                ).to_dict()
            )
        else:
            payload = self._presenter.present(result)

        return json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            indent=indent,
        )
