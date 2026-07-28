import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from hashlib import sha256
from typing import Any

from src.research.specification import (
    ResearchSpecification,
)

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

    research_specification: ResearchSpecification | None = None
    strategy_parameters: dict[str, Any] = field(default_factory=dict)

    tags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        self._validate_required_text()
        self._validate_executor_type()
        self._validate_time_range()
        self._validate_direction()
        self._validate_risk_parameters()
        self._validate_cost_parameters()
        self._validate_research_specification()
        self._validate_strategy_parameters()
        self._validate_tags()

    @property
    def fingerprint(self) -> str:
        payload = json.dumps(
            self._fingerprint_payload(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )

        return sha256(
            payload.encode("utf-8")
        ).hexdigest()

    def _fingerprint_payload(
        self,
    ) -> dict[str, object]:
        return {
            "schema_version": 1,
            "executor_type": self.executor_type.strip(),
            "question_title": self.question_title.strip(),
            "question_description": (
                self.question_description.strip()
            ),
            "hypothesis_title": (
                self.hypothesis_title.strip()
            ),
            "hypothesis_description": (
                self.hypothesis_description.strip()
            ),
            "expected_result": (
                self.expected_result.strip()
            ),
            "experiment_title": (
                self.experiment_title.strip()
            ),
            "experiment_description": (
                self.experiment_description.strip()
            ),
            "data_source": self.data_source.strip(),
            "symbol": self.symbol.strip(),
            "timeframe": self.timeframe.strip(),
            "start_at": self._serialize_datetime(
                self.start_at
            ),
            "end_at": self._serialize_datetime(
                self.end_at
            ),
            "entry_rule": self.entry_rule.strip(),
            "exit_rule": self.exit_rule.strip(),
            "direction": self.direction.value,
            "stop_loss_percent": (
                self.stop_loss_percent
            ),
            "take_profit_percent": (
                self.take_profit_percent
            ),
            "max_holding_bars": (
                self.max_holding_bars
            ),
            "commission_percent": (
                self.commission_percent
            ),
            "slippage_percent": (
                self.slippage_percent
            ),
            "research_specification": (
                self.research_specification.to_dict()
                if self.research_specification
                is not None
                else None
            ),
            "strategy_parameters": dict(
                self.strategy_parameters
            ),
            "tags": sorted(
                tag.strip()
                for tag in self.tags
            ),
        }

    @staticmethod
    def _serialize_datetime(
        value: datetime,
    ) -> str:
        if (
            value.tzinfo is not None
            and value.utcoffset() is not None
        ):
            return value.astimezone(
                timezone.utc
            ).isoformat()

        return value.isoformat()

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

    def _validate_direction(self) -> None:
        if not isinstance(
            self.direction,
            MarketPositionDirection,
        ):
            raise TypeError(
                "direction must be a "
                "MarketPositionDirection"
            )

    def _validate_strategy_parameters(self) -> None:
        if not isinstance(
            self.strategy_parameters,
            dict,
        ):
            raise TypeError(
                "strategy_parameters must be a dictionary"
            )

        for key in self.strategy_parameters:
            if not isinstance(key, str) or not key.strip():
                raise ValueError(
                    "strategy_parameters keys must be "
                    "non-empty strings"
                )

        try:
            json.dumps(
                self.strategy_parameters,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
                allow_nan=False,
            )
        except (TypeError, ValueError) as error:
            raise ValueError(
                "strategy_parameters must be "
                "JSON-compatible"
            ) from error

    def _validate_tags(self) -> None:
        if not isinstance(self.tags, tuple):
            raise TypeError(
                "tags must be a tuple"
            )

        normalized_tags: list[str] = []

        for tag in self.tags:
            if not isinstance(tag, str) or not tag.strip():
                raise ValueError(
                    "tags must contain only non-empty strings"
                )

            normalized_tags.append(
                tag.strip()
            )

        if len(normalized_tags) != len(
            set(normalized_tags)
        ):
            raise ValueError(
                "tags must not contain duplicates"
            )

    def _validate_research_specification(self) -> None:
        if (
            self.research_specification is not None
            and not isinstance(
                self.research_specification,
                ResearchSpecification,
            )
        ):
            raise TypeError(
                "research_specification must be a "
                "ResearchSpecification or None"
            )