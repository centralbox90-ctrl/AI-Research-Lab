from datetime import datetime, timezone
from types import SimpleNamespace

from src.application.indicator_parameter_search_application import (
    IndicatorParameterSearchApplication,
)
from src.application.market_experiment_mapper import (
    MarketExperimentMapper,
)
from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
    MarketPositionDirection,
)
from src.indicators.catalog import IndicatorCatalog
from src.indicators.descriptor import IndicatorDescriptor
from src.indicators.parameter_spaces import (
    ChoiceParameter,
    FloatParameter,
    IntegerParameter,
)
from src.indicators.research_space import (
    IndicatorOutput,
    IndicatorResearchSpace,
)
from src.research.experiment_result import ExperimentResult
from src.research.research_campaign import ResearchCampaign


def calculate(*args: object) -> object:
    raise AssertionError("calculator must not run in orchestration test")


def build_indicator_catalog() -> IndicatorCatalog:
    descriptor = IndicatorDescriptor(
        id="test_indicator",
        symbol="TEST",
        name="Test indicator",
        version=1,
        calculator=calculate,
        research_space=IndicatorResearchSpace(
            outputs=(IndicatorOutput(name="value"),),
            calculation_parameters={
                "period": IntegerParameter(
                    minimum=10,
                    maximum=11,
                    default=10,
                ),
            },
            observation_parameters={
                "level": FloatParameter(
                    minimum=-80.0,
                    maximum=-79.0,
                    default=-80.0,
                ),
                "direction": ChoiceParameter(
                    values=("cross_above",),
                    default="cross_above",
                ),
            },
            observation_types=("level_cross",),
            research_profiles=("test",),
            signal_rule_ids=("indicator_direction",),
        ),
    )
    return IndicatorCatalog((descriptor,))


def build_market_specification() -> MarketExperimentSpecification:
    return MarketExperimentSpecification(
        executor_type="market_backtest",
        question_title="Which parameters work best?",
        question_description="Search an indicator parameter grid.",
        hypothesis_title="Some parameters outperform others",
        hypothesis_description="Compare every declared combination.",
        expected_result="One combination ranks first.",
        experiment_title="Parameter search",
        experiment_description="Run one grid point.",
        data_source="mt5",
        symbol="XAUUSD",
        timeframe="M5",
        start_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        end_at=datetime(2024, 2, 1, tzinfo=timezone.utc),
        entry_rule="indicator signal",
        exit_rule="risk policy",
        direction=MarketPositionDirection.LONG,
        stop_loss_percent=1.0,
        take_profit_percent=1.0,
        max_holding_bars=10,
    )


class RecordingSessionFactory:
    def __init__(self) -> None:
        self.specifications = ()

    def create(self, specifications):
        self.specifications = tuple(specifications)
        mapped = MarketExperimentMapper().map_campaign(
            self.specifications
        )
        campaign = ResearchCampaign(
            title=mapped.question.title,
            hypothesis_id=mapped.hypothesis.id,
        )
        for experiment in mapped.experiments:
            campaign.add_experiment(experiment.id)
        return SimpleNamespace(
            question=mapped.question,
            hypothesis=mapped.hypothesis,
            campaign=campaign,
            experiments=mapped.experiments,
            executor=object(),
        )


class ParameterScoringResearchEngine:
    def run_campaign(
        self,
        *,
        question,
        hypothesis,
        campaign,
        experiments,
        executor,
    ):
        campaign.start()
        cycles = []
        for experiment in experiments:
            specification = experiment.parameters[
                "research_specification"
            ]
            period = specification.calculation_parameter_values[
                "period"
            ]
            level = specification.observation_parameter_values[
                "level"
            ]
            result = ExperimentResult(
                experiment_id=experiment.id,
                success=True,
                metrics={"net_profit": period + level / 100.0},
                observations={},
                conclusion="scored",
            )
            cycles.append(SimpleNamespace(result=result))
        campaign.complete()
        return cycles


def test_application_runs_and_ranks_every_declared_combination() -> None:
    session_factory = RecordingSessionFactory()
    base = build_market_specification()
    application = IndicatorParameterSearchApplication(
        indicator_catalog=build_indicator_catalog(),
        session_factory=session_factory,
        research_engine=ParameterScoringResearchEngine(),
    )

    result = application.run(
        market_specification=base,
        indicator_id="test_indicator",
    )

    assert len(result.cycles) == 4
    assert len(result.ranking) == 4
    assert len(session_factory.specifications) == 4
    assert base.research_specification is None
    assert {
        specification.symbol
        for specification in result.market_specifications
    } == {"XAUUSD"}
    assert (
        result.best_market_specification
        .research_specification
        .calculation_parameter_values["period"]
        == 11
    )
    assert (
        result.best_market_specification
        .research_specification
        .observation_parameter_values["level"]
        == -79.0
    )
