from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
)
from src.research.assumption import (
    Assumption,
    AssumptionSet,
    AssumptionType,
)


def build_assumption_set_from_market_specification(
    specification: MarketExperimentSpecification,
) -> AssumptionSet:
    """
    Builds an immutable assumption set from the current market
    experiment specification.

    This adapter preserves backward compatibility while the project
    transitions to explicit research assumptions.
    """

    assumptions = (
        Assumption(
            id="execution.entry_rule",
            type=AssumptionType.EXECUTION,
            statement="Entry execution rule.",
            value=specification.entry_rule,
        ),
        Assumption(
            id="execution.exit_rule",
            type=AssumptionType.EXECUTION,
            statement="Exit execution rule.",
            value=specification.exit_rule,
        ),
        Assumption(
            id="execution.direction",
            type=AssumptionType.EXECUTION,
            statement="Permitted market-position direction.",
            value=specification.direction.value,
        ),
        Assumption(
            id="execution.stop_loss_percent",
            type=AssumptionType.EXECUTION,
            statement="Stop-loss distance as a percentage.",
            value=specification.stop_loss_percent,
        ),
        Assumption(
            id="execution.take_profit_percent",
            type=AssumptionType.EXECUTION,
            statement="Take-profit distance as a percentage.",
            value=specification.take_profit_percent,
        ),
        Assumption(
            id="execution.max_holding_bars",
            type=AssumptionType.EXECUTION,
            statement="Maximum holding period in bars.",
            value=specification.max_holding_bars,
        ),
        Assumption(
            id="cost.commission_percent",
            type=AssumptionType.COST,
            statement=(
                "Commission is the total round-trip percentage cost."
            ),
            value=specification.commission_percent,
        ),
        Assumption(
            id="cost.slippage_percent",
            type=AssumptionType.COST,
            statement=(
                "Slippage is deterministic and adverse on entry "
                "and exit."
            ),
            value=specification.slippage_percent,
        ),
        Assumption(
            id="execution.intrabar_conflict_policy",
            type=AssumptionType.EXECUTION,
            statement=(
                "Stop loss has priority when stop loss and take "
                "profit are both reached within one bar."
            ),
            value="STOP_LOSS_FIRST",
        ),
        Assumption(
            id="execution.end_of_data_policy",
            type=AssumptionType.EXECUTION,
            statement=(
                "An open position is closed at the final bar close."
            ),
            value="CLOSE_AT_FINAL_BAR",
        ),
        Assumption(
            id="execution.entry_bar_counting",
            type=AssumptionType.EXECUTION,
            statement=(
                "The entry bar is not included in bars held."
            ),
            value="EXCLUDE_ENTRY_BAR",
        ),
        Assumption(
            id="data.source",
            type=AssumptionType.DATA,
            statement="Market data source.",
            value=specification.data_source,
        ),
        Assumption(
            id="scope.symbol",
            type=AssumptionType.SCOPE,
            statement="Research instrument.",
            value=specification.symbol,
        ),
        Assumption(
            id="scope.timeframe",
            type=AssumptionType.SCOPE,
            statement="Research timeframe.",
            value=specification.timeframe,
        ),
        Assumption(
            id="scope.data_interval",
            type=AssumptionType.SCOPE,
            statement="Historical data interval.",
            value={
                "start_at": specification.start_at.isoformat(),
                "end_at": specification.end_at.isoformat(),
            },
        ),
        Assumption(
            id="indicator.strategy_parameters",
            type=AssumptionType.INDICATOR,
            statement="Strategy and indicator parameters.",
            value=dict(specification.strategy_parameters),
        ),
    )

    return AssumptionSet(
        id=(
            f"market-experiment:"
            f"{specification.symbol}:"
            f"{specification.timeframe}:v1"
        ),
        assumptions=assumptions,
    )
