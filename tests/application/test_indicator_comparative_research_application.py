from datetime import UTC, datetime

import pytest

from src.application.indicator_comparative_research_application import (
    IndicatorComparativeResearchApplication,
)
from src.application.indicator_comparative_research_design import (
    IndicatorComparativeResearchDesign,
)
from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
    MarketPositionDirection,
)
from src.indicators.catalog import (
    IndicatorCatalog,
    IndicatorNotFoundError,
)
from src.indicators.implementations.rsi import INDICATOR
from src.research.outcome_specification import (
    ForwardReturnSpecification,
)
from src.research.specification_factory import (
    create_default_research_specification,
)


class StubDatasetProvider:
    def __init__(self, dataset: object) -> None:
        self.dataset = dataset
        self.calls: list[object] = []

    def load(self, specification: object) -> object:
        self.calls.append(specification)
        return self.dataset


class StubComparativeResearchService:
    def __init__(self, analysis: object) -> None:
        self.analysis = analysis
        self.calls: list[dict[str, object]] = []

    def run(
        self,
        *,
        dataset: object,
        design: IndicatorComparativeResearchDesign,
        symbol: str,
        timeframe: str,
    ) -> object:
        self.calls.append(
            {
                "dataset": dataset,
                "design": design,
                "symbol": symbol,
                "timeframe": timeframe,
            }
        )
        return self.analysis


def build_market_specification(
) -> MarketExperimentSpecification:
    return MarketExperimentSpecification(
        executor_type="market_backtest",
        question_title="Can the indicator predict returns?",
        question_description=(
            "Compare indicator observations with a baseline."
        ),
        hypothesis_title="Indicator observations are informative",
        hypothesis_description=(
            "Forward returns differ after observations."
        ),
        expected_result=(
            "Candidate and baseline returns are compared."
        ),
        experiment_title="Comparative indicator research",
        experiment_description=(
            "Run the default indicator research profile."
        ),
        data_source="stub",
        symbol="EURUSD",
        timeframe="H1",
        start_at=datetime(
            2026,
            1,
            1,
            tzinfo=UTC,
        ),
        end_at=datetime(
            2026,
            2,
            1,
            tzinfo=UTC,
        ),
        entry_rule="indicator observation",
        exit_rule="forward horizon",
        direction=MarketPositionDirection.LONG,
        stop_loss_percent=1.0,
        take_profit_percent=2.0,
        max_holding_bars=10,
    )


def build_application(
    *,
    catalog: IndicatorCatalog | None = None,
) -> tuple[
    IndicatorComparativeResearchApplication,
    StubDatasetProvider,
    StubComparativeResearchService,
    object,
    object,
]:
    dataset = object()
    analysis = object()
    provider = StubDatasetProvider(dataset)
    service = StubComparativeResearchService(
        analysis
    )
    application = IndicatorComparativeResearchApplication(
        data_provider=provider,
        indicator_catalog=(
            catalog
            if catalog is not None
            else IndicatorCatalog((INDICATOR,))
        ),
        research_service=service,
    )

    return (
        application,
        provider,
        service,
        dataset,
        analysis,
    )


def test_runs_default_comparative_indicator_research(
) -> None:
    (
        application,
        provider,
        service,
        dataset,
        expected_analysis,
    ) = build_application()
    market_specification = build_market_specification()
    outcome_specification = ForwardReturnSpecification(
        horizons=(1, 3),
    )

    analysis = application.run(
        market_specification=market_specification,
        indicator_id="  rsi  ",
        outcome_specification=outcome_specification,
    )

    assert analysis is expected_analysis
    assert provider.calls == [market_specification]
    assert len(service.calls) == 1

    call = service.calls[0]
    assert call["dataset"] is dataset
    assert call["symbol"] == "EURUSD"
    assert call["timeframe"] == "H1"

    design = call["design"]
    assert isinstance(
        design,
        IndicatorComparativeResearchDesign,
    )
    assert design.outcome_specification is (
        outcome_specification
    )
    assert (
        design.research_specification.fingerprint
        == create_default_research_specification(
            INDICATOR
        ).fingerprint
    )


def test_rejects_unknown_indicator_before_loading_data(
) -> None:
    application, provider, service, _, _ = (
        build_application(
            catalog=IndicatorCatalog(())
        )
    )

    with pytest.raises(
        IndicatorNotFoundError,
        match="Unknown indicator 'rsi'",
    ):
        application.run(
            market_specification=(
                build_market_specification()
            ),
            indicator_id="rsi",
            outcome_specification=(
                ForwardReturnSpecification(
                    horizons=(1,),
                )
            ),
        )

    assert provider.calls == []
    assert service.calls == []


@pytest.mark.parametrize(
    ("field_name", "invalid_value", "error_type", "message"),
    (
        (
            "market_specification",
            object(),
            TypeError,
            "market_specification must be a "
            "MarketExperimentSpecification",
        ),
        (
            "indicator_id",
            object(),
            TypeError,
            "indicator_id must be a string",
        ),
        (
            "indicator_id",
            "   ",
            ValueError,
            "indicator_id must not be empty",
        ),
        (
            "outcome_specification",
            object(),
            TypeError,
            "outcome_specification must be a "
            "ForwardReturnSpecification",
        ),
    ),
)
def test_rejects_invalid_arguments(
    field_name: str,
    invalid_value: object,
    error_type: type[Exception],
    message: str,
) -> None:
    application, provider, service, _, _ = (
        build_application()
    )
    arguments = {
        "market_specification": (
            build_market_specification()
        ),
        "indicator_id": "rsi",
        "outcome_specification": (
            ForwardReturnSpecification(
                horizons=(1,),
            )
        ),
    }
    arguments[field_name] = invalid_value

    with pytest.raises(
        error_type,
        match=message,
    ):
        application.run(**arguments)

    assert provider.calls == []
    assert service.calls == []
