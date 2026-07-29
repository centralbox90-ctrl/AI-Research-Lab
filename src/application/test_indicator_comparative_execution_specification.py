from dataclasses import replace
from datetime import UTC, datetime

import pytest

from src.application.indicator_comparative_execution_specification import (
    IndicatorComparativeExecutionSpecification,
)
from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
    MarketPositionDirection,
)
from src.research.outcome_specification import (
    ForwardReturnSpecification,
)
from src.research.specification import (
    IndicatorReference,
    ResearchSpecification,
)


def build_market_specification(
) -> MarketExperimentSpecification:
    return MarketExperimentSpecification(
        executor_type="market_backtest",
        question_title="Does RSI predict returns?",
        question_description=(
            "Test RSI on generated market data."
        ),
        hypothesis_title="RSI predicts returns",
        hypothesis_description=(
            "Returns differ after RSI observations."
        ),
        expected_result=(
            "A measurable return difference."
        ),
        experiment_title=(
            "Comparative RSI experiment"
        ),
        experiment_description=(
            "Compare RSI observations with a baseline."
        ),
        data_source="generated",
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
        entry_rule="unused_entry",
        exit_rule="unused_exit",
        direction=MarketPositionDirection.LONG,
        stop_loss_percent=1.0,
        take_profit_percent=2.0,
        max_holding_bars=24,
        strategy_parameters={
            "unused": True,
        },
    )


def build_research_specification(
    indicator_id: str = "rsi",
) -> ResearchSpecification:
    return ResearchSpecification.create(
        indicator=IndicatorReference(
            indicator_id=indicator_id,
            indicator_version=1,
        ),
        output="value",
        profile=None,
        observation_type="direction",
        calculation_parameters={
            "period": 14,
        },
        observation_parameters={},
    )


def build_execution_specification(
) -> IndicatorComparativeExecutionSpecification:
    return (
        IndicatorComparativeExecutionSpecification(
            market_specification=(
                build_market_specification()
            ),
            research_specification=(
                build_research_specification()
            ),
            outcome_specification=(
                ForwardReturnSpecification(
                    horizons=(1, 3),
                    price_field="close",
                )
            ),
        )
    )


def test_serializes_consumed_execution_inputs(
) -> None:
    specification = (
        build_execution_specification()
    )

    assert specification.to_dict() == {
        "schema_version": 1,
        "execution_type": (
            "indicator_comparative_research"
        ),
        "market_data": {
            "data_source": "generated",
            "symbol": "EURUSD",
            "timeframe": "H1",
            "start_at": (
                "2026-01-01T00:00:00+00:00"
            ),
            "end_at": (
                "2026-02-01T00:00:00+00:00"
            ),
        },
        "research_specification": (
            specification
            .research_specification
            .to_dict()
        ),
        "outcome_specification": {
            "horizons": [1, 3],
            "price_field": "close",
        },
        "baseline": "unconditional",
    }


def test_fingerprint_is_deterministic_sha256(
) -> None:
    first = build_execution_specification()
    second = build_execution_specification()

    assert first.fingerprint == second.fingerprint
    assert len(first.fingerprint) == 64
    assert set(first.fingerprint) <= set(
        "0123456789abcdef"
    )


def test_fingerprint_tracks_consumed_inputs(
) -> None:
    specification = (
        build_execution_specification()
    )
    changed_market = replace(
        specification,
        market_specification=replace(
            specification.market_specification,
            end_at=datetime(
                2026,
                3,
                1,
                tzinfo=UTC,
            ),
        ),
    )
    changed_research = replace(
        specification,
        research_specification=(
            build_research_specification("ema")
        ),
    )
    changed_outcome = replace(
        specification,
        outcome_specification=(
            ForwardReturnSpecification(
                horizons=(1, 5),
            )
        ),
    )

    assert changed_market.fingerprint != (
        specification.fingerprint
    )
    assert changed_research.fingerprint != (
        specification.fingerprint
    )
    assert changed_outcome.fingerprint != (
        specification.fingerprint
    )


def test_fingerprint_ignores_unused_backtest_settings(
) -> None:
    specification = (
        build_execution_specification()
    )
    changed_market = replace(
        specification.market_specification,
        entry_rule="different_unused_entry",
        exit_rule="different_unused_exit",
        take_profit_percent=5.0,
        strategy_parameters={
            "different": True,
        },
    )
    changed_specification = replace(
        specification,
        market_specification=changed_market,
    )

    assert changed_specification.fingerprint == (
        specification.fingerprint
    )


@pytest.mark.parametrize(
    ("field_name", "value", "message"),
    (
        (
            "market_specification",
            object(),
            (
                "market_specification must be a "
                "MarketExperimentSpecification"
            ),
        ),
        (
            "research_specification",
            object(),
            (
                "research_specification must be a "
                "ResearchSpecification"
            ),
        ),
        (
            "outcome_specification",
            object(),
            (
                "outcome_specification must be a "
                "ForwardReturnSpecification"
            ),
        ),
    ),
)
def test_rejects_invalid_component_types(
    field_name: str,
    value: object,
    message: str,
) -> None:
    values = {
        "market_specification": (
            build_market_specification()
        ),
        "research_specification": (
            build_research_specification()
        ),
        "outcome_specification": (
            ForwardReturnSpecification(
                horizons=(1, 3),
            )
        ),
    }
    values[field_name] = value

    with pytest.raises(
        TypeError,
        match=message,
    ):
        IndicatorComparativeExecutionSpecification(
            **values,
        )


def test_requires_unconditional_baseline(
) -> None:
    with pytest.raises(
        ValueError,
        match="baseline must be 'unconditional'",
    ):
        replace(
            build_execution_specification(),
            baseline="matched",
        )
