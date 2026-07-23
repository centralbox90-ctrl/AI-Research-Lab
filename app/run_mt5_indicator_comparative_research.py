from __future__ import annotations

import json
from argparse import (
    ArgumentParser,
    ArgumentTypeError,
    Namespace,
)
from collections.abc import Sequence
from datetime import UTC, datetime

from src.application.canonical_market_data_provider import (
    CanonicalMarketDataProvider,
)
from src.application.indicator_comparative_research_application import (
    IndicatorComparativeResearchApplication,
)
from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
    MarketPositionDirection,
)
from src.application.mt5_market_data_provider import (
    Mt5MarketDataProvider,
)
from src.cli.indicator_comparative_research_composition_root import (
    build_default_indicator_comparative_research_application,
)
from src.cli.indicator_comparative_research_presenter import (
    present_indicator_comparative_research_result,
)
from src.research.outcome_specification import (
    ForwardReturnSpecification,
)


_DEFAULT_HORIZONS = (1, 3, 5)


def build_argument_parser() -> ArgumentParser:
    parser = ArgumentParser(
        description=(
            "Run comparative indicator research "
            "on canonical MT5 market data."
        )
    )
    parser.add_argument(
        "--indicator",
        default="rsi",
        type=_parse_non_empty_text,
    )
    parser.add_argument(
        "--symbol",
        required=True,
        type=_parse_non_empty_text,
    )
    parser.add_argument(
        "--timeframe",
        default="H1",
        type=_parse_non_empty_text,
    )
    parser.add_argument(
        "--start-at",
        required=True,
        type=_parse_utc_datetime,
    )
    parser.add_argument(
        "--end-at",
        required=True,
        type=_parse_utc_datetime,
    )
    parser.add_argument(
        "--horizon",
        action="append",
        dest="horizons",
        type=_parse_positive_integer,
    )
    parser.add_argument(
        "--indent",
        default=2,
        type=_parse_nonnegative_integer,
    )

    return parser


def parse_arguments(
    arguments: Sequence[str] | None = None,
) -> Namespace:
    parser = build_argument_parser()
    parsed = parser.parse_args(arguments)

    if parsed.start_at >= parsed.end_at:
        parser.error(
            "--start-at must be earlier than --end-at"
        )

    if parsed.horizons is None:
        parsed.horizons = list(
            _DEFAULT_HORIZONS
        )

    return parsed


def build_market_specification(
    arguments: Namespace,
) -> MarketExperimentSpecification:
    indicator_id = arguments.indicator.strip()
    symbol = arguments.symbol.strip().upper()
    timeframe = arguments.timeframe.strip().upper()

    return MarketExperimentSpecification(
        executor_type="market_backtest",
        question_title=(
            f"Does {indicator_id} identify "
            "forward-return differences?"
        ),
        question_description=(
            "Compare indicator observations with "
            "the canonical market baseline."
        ),
        hypothesis_title=(
            f"{indicator_id} observations differ "
            "from the market baseline"
        ),
        hypothesis_description=(
            "Forward returns following indicator "
            "observations differ from baseline returns."
        ),
        expected_result=(
            "A reproducible comparative analysis "
            "for every requested horizon."
        ),
        experiment_title=(
            f"{indicator_id} comparative research"
        ),
        experiment_description=(
            "Comparative indicator research using "
            "closed canonical MT5 candles."
        ),
        data_source="mt5",
        symbol=symbol,
        timeframe=timeframe,
        start_at=arguments.start_at,
        end_at=arguments.end_at,
        entry_rule=(
            "Not used by comparative indicator research"
        ),
        exit_rule=(
            "Not used by comparative indicator research"
        ),
        direction=MarketPositionDirection.LONG,
        stop_loss_percent=1.0,
        take_profit_percent=1.0,
        max_holding_bars=1,
        strategy_parameters={},
        tags=(
            "mt5",
            "comparative-research",
            indicator_id,
        ),
    )


def build_application(
) -> IndicatorComparativeResearchApplication:
    data_provider = CanonicalMarketDataProvider(
        Mt5MarketDataProvider()
    )

    return (
        build_default_indicator_comparative_research_application(
            data_provider=data_provider,
        )
    )


def execute_comparative_research(
    *,
    arguments: Namespace,
    application: IndicatorComparativeResearchApplication,
) -> dict[str, object]:
    result = application.run(
        market_specification=(
            build_market_specification(arguments)
        ),
        indicator_id=arguments.indicator,
        outcome_specification=(
            ForwardReturnSpecification(
                horizons=tuple(arguments.horizons),
            )
        ),
    )

    return (
        present_indicator_comparative_research_result(
            result
        )
    )


def main(
    arguments: Sequence[str] | None = None,
) -> int:
    parsed = parse_arguments(arguments)
    payload = execute_comparative_research(
        arguments=parsed,
        application=build_application(),
    )

    print(
        json.dumps(
            payload,
            indent=parsed.indent,
            sort_keys=True,
            ensure_ascii=False,
            allow_nan=False,
        )
    )

    return 0


def _parse_non_empty_text(value: str) -> str:
    normalized = value.strip()

    if not normalized:
        raise ArgumentTypeError(
            "value must not be empty"
        )

    return normalized


def _parse_utc_datetime(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )
    except ValueError as error:
        raise ArgumentTypeError(
            "value must be an ISO-8601 datetime"
        ) from error

    if parsed.tzinfo is None:
        raise ArgumentTypeError(
            "datetime must include a timezone"
        )

    return parsed.astimezone(UTC)


def _parse_positive_integer(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as error:
        raise ArgumentTypeError(
            "value must be an integer"
        ) from error

    if parsed < 1:
        raise ArgumentTypeError(
            "value must be positive"
        )

    return parsed


def _parse_nonnegative_integer(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as error:
        raise ArgumentTypeError(
            "value must be an integer"
        ) from error

    if parsed < 0:
        raise ArgumentTypeError(
            "value must not be negative"
        )

    return parsed


if __name__ == "__main__":
    raise SystemExit(main())
