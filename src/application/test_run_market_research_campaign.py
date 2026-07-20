from src.application.run_market_research_campaign import (
    RunMarketResearchCampaign,
)


class FakeCampaignSession:
    def __init__(self) -> None:
        self.question = object()
        self.hypothesis = object()
        self.campaign = object()
        self.experiments = (
            object(),
            object(),
        )
        self.executor = object()


class FakeCampaignSessionFactory:
    def __init__(self) -> None:
        self.received_specifications = None
        self.session = FakeCampaignSession()

    def create(self, specifications):
        self.received_specifications = specifications

        return self.session


class FakeResearchEngine:
    def __init__(self) -> None:
        self.received_arguments = None
        self.results = [
            object(),
            object(),
        ]

    def run_campaign(
        self,
        *,
        question,
        hypothesis,
        campaign,
        experiments,
        executor,
    ):
        self.received_arguments = {
            "question": question,
            "hypothesis": hypothesis,
            "campaign": campaign,
            "experiments": experiments,
            "executor": executor,
        }

        return self.results


def test_run_executes_prepared_campaign() -> None:
    factory = FakeCampaignSessionFactory()
    engine = FakeResearchEngine()

    use_case = RunMarketResearchCampaign(
        session_factory=factory,
        engine=engine,
    )

    specifications = (
        object(),
        object(),
    )

    results = use_case.run(
        specifications,
    )

    assert factory.received_specifications is specifications

    assert engine.received_arguments == {
        "question": factory.session.question,
        "hypothesis": factory.session.hypothesis,
        "campaign": factory.session.campaign,
        "experiments": list(
            factory.session.experiments
        ),
        "executor": factory.session.executor,
    }

    assert results is engine.results