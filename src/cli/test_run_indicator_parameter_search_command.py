import json
from dataclasses import replace
from types import SimpleNamespace

from src.cli.run_indicator_parameter_search_command import (
    RunIndicatorParameterSearchCommand,
)
from src.research.experiment import Experiment
from src.research.experiment_comparator import RankedExperiment
from src.research.experiment_result import ExperimentResult
from src.research.research_campaign import ResearchCampaign
from src.research.research_types import ResearchStatus
from src.research.specification import (
    IndicatorReference,
    ResearchSpecification,
)


class StubApplication:
    def __init__(self) -> None:
        self.market_specification = None

    def run(
        self,
        *,
        market_specification,
        indicator_id,
        metric="net_profit",
        reverse=True,
    ):
        self.market_specification = market_specification
        research = ResearchSpecification.create(
            indicator=IndicatorReference(
                indicator_id=indicator_id,
                indicator_version=1,
            ),
            output="value",
            profile="oscillator",
            observation_type="band_reentry",
            signal_rule_id="indicator_direction",
            calculation_parameters={"period": 12},
            observation_parameters={
                "lower_level": -70.0,
                "upper_level": -30.0,
            },
        )
        specification = replace(
            market_specification,
            research_specification=research,
        )
        experiment = Experiment(
            hypothesis_id="hypothesis-1",
            title="grid point",
        )
        result = ExperimentResult(
            experiment_id=experiment.id,
            success=True,
            metrics={"net_profit": 3.5, "total_trades": 42},
            observations={},
            conclusion="best",
        )
        ranked = RankedExperiment(
            experiment=experiment,
            result=result,
            score=3.5,
        )
        campaign = ResearchCampaign(
            id="campaign-1",
            title="search",
            hypothesis_id="hypothesis-1",
            experiment_ids=[experiment.id],
            status=ResearchStatus.COMPLETED,
        )
        return SimpleNamespace(
            indicator_id=indicator_id,
            metric=metric,
            session=SimpleNamespace(
                campaign=campaign,
                experiments=(experiment,),
            ),
            market_specifications=(specification,),
            ranking=(ranked,),
            best=ranked,
        )


def test_command_builds_mt5_campaign_and_presents_best() -> None:
    application = StubApplication()
    command = RunIndicatorParameterSearchCommand(
        application=application
    )

    rendered = command.execute(
        indicator_id="williams_r",
        symbol="XAUUSD",
        timeframe="M5",
        start_at="2025-01-01",
        end_at="2025-07-01",
    )

    payload = json.loads(rendered)
    assert payload["campaign_id"] == "campaign-1"
    assert payload["campaign_status"] == "COMPLETED"
    assert payload["best"]["score"] == 3.5
    assert payload["best"]["calculation_parameters"] == {
        "period": 12,
    }
    assert payload["best"]["observation_parameters"] == {
        "lower_level": -70.0,
        "upper_level": -30.0,
    }
    assert application.market_specification.data_source == "mt5"
    assert application.market_specification.symbol == "XAUUSD"
    assert application.market_specification.timeframe == "M5"
