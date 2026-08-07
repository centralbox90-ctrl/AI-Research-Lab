from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Protocol

from src.application.indicator_parameter_search_application import (
    IndicatorParameterSearchResult,
)
from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
    MarketPositionDirection,
)


class IndicatorParameterSearchRunner(Protocol):
    def run(
        self,
        *,
        market_specification: MarketExperimentSpecification,
        indicator_id: str,
        metric: str = "net_profit",
        reverse: bool = True,
    ) -> IndicatorParameterSearchResult:
        ...


class RunIndicatorParameterSearchCommand:
    """Build and run one generic indicator parameter campaign."""

    def __init__(
        self,
        *,
        application: IndicatorParameterSearchRunner,
    ) -> None:
        if not callable(getattr(application, "run", None)):
            raise TypeError("application must provide run()")
        self._application = application

    def execute(
        self,
        *,
        indicator_id: str,
        symbol: str,
        timeframe: str,
        start_at: str,
        end_at: str,
        stop_loss_percent: float = 1.0,
        take_profit_percent: float = 2.0,
        max_holding_bars: int = 24,
        commission_percent: float = 0.0,
        slippage_percent: float = 0.0,
        metric: str = "net_profit",
        top: int = 20,
        indent: int | None = 2,
    ) -> str:
        if isinstance(top, bool) or not isinstance(top, int) or top < 1:
            raise ValueError("top must be a positive integer")

        normalized_indicator_id = self._normalize_text(
            indicator_id,
            "indicator_id",
        )
        normalized_symbol = self._normalize_text(symbol, "symbol")
        normalized_timeframe = self._normalize_text(
            timeframe,
            "timeframe",
        )
        start = self._parse_timestamp(start_at, "start_at")
        end = self._parse_timestamp(end_at, "end_at")

        market_specification = MarketExperimentSpecification(
            executor_type="market_backtest",
            question_title=(
                f"Which {normalized_indicator_id} parameters work "
                f"best on {normalized_symbol} {normalized_timeframe}?"
            ),
            question_description=(
                "Evaluate every parameter combination declared by "
                "the indicator plugin."
            ),
            hypothesis_title=(
                f"{normalized_indicator_id} contains a reproducible "
                "parameter region"
            ),
            hypothesis_description=(
                "At least one declared parameter combination produces "
                "stronger market results than the alternatives."
            ),
            expected_result=(
                "Rank all declared combinations by the selected metric."
            ),
            experiment_title=(
                f"{normalized_indicator_id} parameter search"
            ),
            experiment_description=(
                "Execute one point from the indicator research space."
            ),
            data_source="mt5",
            symbol=normalized_symbol,
            timeframe=normalized_timeframe,
            start_at=start,
            end_at=end,
            entry_rule="indicator plugin signal",
            exit_rule="risk and holding policy",
            direction=MarketPositionDirection.LONG,
            stop_loss_percent=stop_loss_percent,
            take_profit_percent=take_profit_percent,
            max_holding_bars=max_holding_bars,
            commission_percent=commission_percent,
            slippage_percent=slippage_percent,
            tags=(
                "indicator-parameter-search",
                normalized_indicator_id,
                "mt5",
            ),
        )
        result = self._application.run(
            market_specification=market_specification,
            indicator_id=normalized_indicator_id,
            metric=metric,
        )

        ranking = tuple(result.ranking[:top])
        specifications_by_experiment_id = {
            experiment.id: specification
            for experiment, specification in zip(
                result.session.experiments,
                result.market_specifications,
                strict=True,
            )
        }

        payload = {
            "campaign_id": result.session.campaign.id,
            "campaign_status": result.session.campaign.status.value,
            "indicator_id": result.indicator_id,
            "symbol": normalized_symbol,
            "timeframe": normalized_timeframe,
            "start_at": start.isoformat(),
            "end_at": end.isoformat(),
            "metric": result.metric,
            "specification_count": len(result.market_specifications),
            "best": self._present_ranked(
                result.best,
                specifications_by_experiment_id,
            ),
            "ranking": [
                self._present_ranked(
                    ranked,
                    specifications_by_experiment_id,
                )
                for ranked in ranking
            ],
        }
        return json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            indent=indent,
        )

    @staticmethod
    def _present_ranked(
        ranked: object,
        specifications_by_experiment_id: dict[
            str,
            MarketExperimentSpecification,
        ],
    ) -> dict[str, object]:
        experiment = ranked.experiment
        specification = specifications_by_experiment_id[
            experiment.id
        ]
        research = specification.research_specification
        if research is None:
            raise RuntimeError(
                "ranked experiment has no research specification"
            )

        return {
            "experiment_id": experiment.id,
            "result_id": ranked.result.id,
            "score": ranked.score,
            "calculation_parameters": (
                research.calculation_parameter_values
            ),
            "observation_parameters": (
                research.observation_parameter_values
            ),
            "metrics": dict(ranked.result.metrics),
        }

    @staticmethod
    def _parse_timestamp(value: object, field_name: str) -> datetime:
        normalized = RunIndicatorParameterSearchCommand._normalize_text(
            value,
            field_name,
        )
        try:
            timestamp = datetime.fromisoformat(normalized)
        except ValueError as error:
            raise ValueError(
                f"{field_name} must be an ISO-8601 timestamp"
            ) from error

        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)

        return timestamp.astimezone(timezone.utc)

    @staticmethod
    def _normalize_text(value: object, field_name: str) -> str:
        if not isinstance(value, str):
            raise TypeError(f"{field_name} must be a string")
        normalized = value.strip()
        if not normalized:
            raise ValueError(f"{field_name} must not be empty")
        return normalized
