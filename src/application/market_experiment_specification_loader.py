import json
from datetime import datetime
from json import JSONDecodeError
from pathlib import Path
from typing import Any

from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
    MarketPositionDirection,
)


class MarketExperimentSpecificationLoader:
    """
    Loads and validates a market experiment specification from JSON.

    The loader converts external JSON values into the typed application
    contract. It does not create executors, run research cycles, access
    market data, or depend on CLI parsing.
    """

    _REQUIRED_FIELDS = {
        "executor_type",
        "question_title",
        "question_description",
        "hypothesis_title",
        "hypothesis_description",
        "expected_result",
        "experiment_title",
        "experiment_description",
        "data_source",
        "symbol",
        "timeframe",
        "start_at",
        "end_at",
        "entry_rule",
        "exit_rule",
        "direction",
        "stop_loss_percent",
        "take_profit_percent",
        "max_holding_bars",
    }

    _OPTIONAL_FIELDS = {
        "commission_percent",
        "slippage_percent",
        "strategy_parameters",
        "tags",
    }

    def load(
        self,
        path: str | Path,
    ) -> MarketExperimentSpecification:
        """
        Load a specification from a UTF-8 JSON file.
        """
        specification_path = Path(path)

        try:
            source = specification_path.read_text(
                encoding="utf-8",
            )
        except OSError as error:
            raise ValueError(
                f"unable to read specification file: "
                f"{specification_path}"
            ) from error

        try:
            payload = json.loads(source)
        except JSONDecodeError as error:
            raise ValueError(
                f"invalid specification JSON: {error.msg}"
            ) from error

        return self.from_dict(payload)

    def from_dict(
        self,
        payload: Any,
    ) -> MarketExperimentSpecification:
        """
        Convert a decoded JSON object into a typed specification.
        """
        if not isinstance(payload, dict):
            raise ValueError(
                "specification JSON must contain an object"
            )

        self._validate_fields(payload)

        strategy_parameters = payload.get(
            "strategy_parameters",
            {},
        )

        if not isinstance(strategy_parameters, dict):
            raise ValueError(
                "strategy_parameters must be an object"
            )

        tags = payload.get("tags", [])

        if not isinstance(tags, list):
            raise ValueError("tags must be an array")

        return MarketExperimentSpecification(
            executor_type=payload["executor_type"],
            question_title=payload["question_title"],
            question_description=payload[
                "question_description"
            ],
            hypothesis_title=payload["hypothesis_title"],
            hypothesis_description=payload[
                "hypothesis_description"
            ],
            expected_result=payload["expected_result"],
            experiment_title=payload["experiment_title"],
            experiment_description=payload[
                "experiment_description"
            ],
            data_source=payload["data_source"],
            symbol=payload["symbol"],
            timeframe=payload["timeframe"],
            start_at=self._parse_datetime(
                field_name="start_at",
                value=payload["start_at"],
            ),
            end_at=self._parse_datetime(
                field_name="end_at",
                value=payload["end_at"],
            ),
            entry_rule=payload["entry_rule"],
            exit_rule=payload["exit_rule"],
            direction=self._parse_direction(
                payload["direction"],
            ),
            stop_loss_percent=payload["stop_loss_percent"],
            take_profit_percent=payload[
                "take_profit_percent"
            ],
            max_holding_bars=payload["max_holding_bars"],
            commission_percent=payload.get(
                "commission_percent",
                0.0,
            ),
            slippage_percent=payload.get(
                "slippage_percent",
                0.0,
            ),
            strategy_parameters=dict(strategy_parameters),
            tags=tuple(tags),
        )

    def _validate_fields(
        self,
        payload: dict[str, Any],
    ) -> None:
        missing_fields = sorted(
            self._REQUIRED_FIELDS - payload.keys()
        )

        if missing_fields:
            raise ValueError(
                "missing specification fields: "
                + ", ".join(missing_fields)
            )

        supported_fields = (
            self._REQUIRED_FIELDS
            | self._OPTIONAL_FIELDS
        )

        unknown_fields = sorted(
            payload.keys() - supported_fields
        )

        if unknown_fields:
            raise ValueError(
                "unknown specification fields: "
                + ", ".join(unknown_fields)
            )

    def _parse_datetime(
        self,
        field_name: str,
        value: Any,
    ) -> datetime:
        if not isinstance(value, str):
            raise ValueError(
                f"{field_name} must be an ISO 8601 string"
            )

        normalized_value = value

        if normalized_value.endswith("Z"):
            normalized_value = (
                normalized_value[:-1] + "+00:00"
            )

        try:
            return datetime.fromisoformat(
                normalized_value,
            )
        except ValueError as error:
            raise ValueError(
                f"{field_name} must be a valid ISO 8601 datetime"
            ) from error

    def _parse_direction(
        self,
        value: Any,
    ) -> MarketPositionDirection:
        if not isinstance(value, str):
            raise ValueError(
                "direction must be 'LONG' or 'SHORT'"
            )

        try:
            return MarketPositionDirection(value)
        except ValueError as error:
            raise ValueError(
                "direction must be 'LONG' or 'SHORT'"
            ) from error