from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any


class MarketPositionDirection(StrEnum):
    """
    Supported market-position directions for a market experiment.
    """

    LONG = "LONG"
    SHORT = "SHORT"


@dataclass(frozen=True)
class MarketExperimentSpecification:
    """
    Declarative specification of a market research experiment.

    The specification contains application-level market settings.
    It does not contain executable Python code and does not depend on
    CLI, JSON, storage, backtest infrastructure, or research-core
    implementation details.
    """

    executor_type: str

    question_title: str
    question_description: str

    hypothesis_title: str
    hypothesis_description: str
    expected_result: str

    experiment_title: str
    experiment_description: str

    data_source: str
    symbol: str
    timeframe: str
    start_at: datetime
    end_at: datetime

    entry_rule: str
    exit_rule: str
    direction: MarketPositionDirection

    stop_loss_percent: float
    take_profit_percent: float
    max_holding_bars: int

    commission_percent: float = 0.0
    slippage_percent: float = 0.0

    strategy_parameters: dict[str, Any] = field(default_factory=dict)

    tags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        self._validate_required_text()
        self._validate_executor_type()
        self._validate_time_range()
        self._validate_risk_parameters()
        self._validate_cost_parameters()
        self._validate_tags()

    def _validate_required_text(self) -> None:
        required_text_fields = {
            "executor_type": self.executor_type,
            "question_title": self.question_title,
            "question_description": self.question_description,
            "hypothesis_title": self.hypothesis_title,
            "hypothesis_description": self.hypothesis_description,
            "expected_result": self.expected_result,
            "experiment_title": self.experiment_title,
            "experiment_description": self.experiment_description,
            "data_source": self.data_source,
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "entry_rule": self.entry_rule,
            "exit_rule": self.exit_rule,
        }

        for field_name, value in required_text_fields.items():
            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"{field_name} must be a non-empty string"
                )

    def _validate_executor_type(self) -> None:
        if self.executor_type != "market_backtest":
            raise ValueError(
                "executor_type must be 'market_backtest'"
            )

    def _validate_time_range(self) -> None:
        if not isinstance(self.start_at, datetime):
            raise ValueError("start_at must be a datetime")

        if not isinstance(self.end_at, datetime):
            raise ValueError("end_at must be a datetime")

        start_is_aware = self.start_at.tzinfo is not None
        end_is_aware = self.end_at.tzinfo is not None

        if start_is_aware != end_is_aware:
            raise ValueError(
                "start_at and end_at must use the same timezone style"
            )

        if self.start_at >= self.end_at:
            raise ValueError("start_at must be earlier than end_at")

    def _validate_risk_parameters(self) -> None:
        if self.stop_loss_percent <= 0:
            raise ValueError(
                "stop_loss_percent must be greater than zero"
            )

        if self.take_profit_percent <= 0:
            raise ValueError(
                "take_profit_percent must be greater than zero"
            )

        if isinstance(self.max_holding_bars, bool):
            raise ValueError(
                "max_holding_bars must be a positive integer"
            )

        if (
            not isinstance(self.max_holding_bars, int)
            or self.max_holding_bars <= 0
        ):
            raise ValueError(
                "max_holding_bars must be a positive integer"
            )

    def _validate_cost_parameters(self) -> None:
        if self.commission_percent < 0:
            raise ValueError(
                "commission_percent must not be negative"
            )

        if self.slippage_percent < 0:
            raise ValueError(
                "slippage_percent must not be negative"
            )

    def _validate_tags(self) -> None:
        for tag in self.tags:
            if not isinstance(tag, str) or not tag.strip():
                raise ValueError(
                    "tags must contain only non-empty strings"
                )