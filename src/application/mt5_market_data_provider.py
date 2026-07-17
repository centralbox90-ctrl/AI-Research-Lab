from __future__ import annotations

from src.application.clock import Clock
from src.application.system_clock import SystemClock

from datetime import datetime, timedelta, timezone
from typing import Any

import MetaTrader5 as mt5
import pandas as pd

from src.application.market_data_provider import (
    MarketDataProvider,
)
from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
)


class Mt5MarketDataProviderError(RuntimeError):
    """
    Raised when MT5 cannot provide valid historical market data.
    """


class Mt5MarketDataProvider(
    MarketDataProvider,
):
    """
    Loads closed historical candles from an installed MT5 terminal.

    The adapter only supplies market data. It does not generate signals,
    execute trades, evaluate hypotheses, or run research cycles.
    """

    def __init__(
        self,
        mt5_module: Any = mt5,
        clock: Clock | None = None,
    ) -> None:
        self._mt5 = mt5_module
        self._clock = clock or SystemClock()

    def load(
        self,
        specification: MarketExperimentSpecification,
    ) -> pd.DataFrame:
        """
        Load closed MT5 candles using the experiment specification.
        """

        timeframe = self._resolve_timeframe(
            specification.timeframe,
        )
        timeframe_duration = self._resolve_timeframe_duration(
            specification.timeframe,
        )

        start_at_utc = self._to_utc(specification.start_at)
        end_at_utc = self._to_utc(specification.end_at)

        if not self._mt5.initialize():
            raise Mt5MarketDataProviderError(
                self._format_mt5_error(
                    "Could not initialize MetaTrader 5",
                )
            )

        try:
            self._ensure_symbol_available(
                specification.symbol,
            )

            rates = self._mt5.copy_rates_range(
                specification.symbol,
                timeframe,
                start_at_utc,
                end_at_utc,
            )

            if rates is None:
                raise Mt5MarketDataProviderError(
                    self._format_mt5_error(
                        "MT5 failed to load historical candles",
                    )
                )

            if len(rates) == 0:
                raise Mt5MarketDataProviderError(
                    "MT5 returned no historical candles for "
                    f"{specification.symbol} "
                    f"{specification.timeframe} "
                    f"from {start_at_utc.isoformat()} "
                    f"to {end_at_utc.isoformat()}"
                )

            data = self._build_dataframe(
                rates=rates,
                specification=specification,
                start_at_utc=start_at_utc,
                end_at_utc=end_at_utc,
                timeframe_duration=timeframe_duration,
            )

            if data.empty:
                raise Mt5MarketDataProviderError(
                    "MT5 returned no closed candles inside the "
                    "requested experiment interval"
                )

            self._validate_dataframe(data)

            data.attrs["provenance"] = self._build_provenance(
                specification=specification,
                data=data,
                start_at_utc=start_at_utc,
                end_at_utc=end_at_utc,
            )

            return data

        finally:
            self._mt5.shutdown()

    def _ensure_symbol_available(
        self,
        symbol: str,
    ) -> None:
        symbol_info = self._mt5.symbol_info(symbol)

        if symbol_info is None:
            raise Mt5MarketDataProviderError(
                self._format_mt5_error(
                    f"MT5 symbol {symbol!r} was not found",
                )
            )

        if not symbol_info.visible:
            if not self._mt5.symbol_select(symbol, True):
                raise Mt5MarketDataProviderError(
                    self._format_mt5_error(
                        f"Could not add MT5 symbol {symbol!r} "
                        "to Market Watch",
                    )
                )

    def _build_dataframe(
        self,
        *,
        rates: Any,
        specification: MarketExperimentSpecification,
        start_at_utc: datetime,
        end_at_utc: datetime,
        timeframe_duration: timedelta,
    ) -> pd.DataFrame:
        data = pd.DataFrame(rates)

        required_columns = {
            "time",
            "open",
            "high",
            "low",
            "close",
            "tick_volume",
        }

        missing_columns = required_columns.difference(data.columns)

        if missing_columns:
            raise Mt5MarketDataProviderError(
                "MT5 response is missing required columns: "
                + ", ".join(sorted(missing_columns))
            )

        timestamps = pd.to_datetime(
            data["time"],
            unit="s",
            utc=True,
        )

        data.index = timestamps
        data.index.name = None

        # The experiment interval is interpreted as:
        # start_at inclusive, end_at exclusive.
        data = data.loc[
            (data.index >= start_at_utc)
            & (
                data.index + timeframe_duration
                <= end_at_utc
            )
        ].copy()

        data = data.sort_index()

        data = data.loc[
            ~data.index.duplicated(keep=False)
        ].copy()

        data["symbol"] = specification.symbol
        data["timeframe"] = specification.timeframe

        data["bar_id"] = [
            (
                f"{specification.symbol}|"
                f"{specification.timeframe}|"
                f"{timestamp.isoformat()}"
            )
            for timestamp in data.index
        ]

        data["Open"] = data["open"].astype(float)
        data["High"] = data["high"].astype(float)
        data["Low"] = data["low"].astype(float)
        data["Close"] = data["close"].astype(float)
        data["Volume"] = data["tick_volume"].astype(int)

        if "spread" in data.columns:
            data["Spread"] = data["spread"].astype(int)

        if "real_volume" in data.columns:
            data["RealVolume"] = data["real_volume"].astype(int)

        output_columns = [
            "symbol",
            "timeframe",
            "bar_id",
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
        ]

        if "Spread" in data.columns:
            output_columns.append("Spread")

        if "RealVolume" in data.columns:
            output_columns.append("RealVolume")

        return data[output_columns]

    def _validate_dataframe(
        self,
        data: pd.DataFrame,
    ) -> None:
        if not data.index.is_monotonic_increasing:
            raise Mt5MarketDataProviderError(
                "MT5 candles are not sorted by time"
            )

        if not data.index.is_unique:
            raise Mt5MarketDataProviderError(
                "MT5 candles contain duplicate timestamps"
            )

        if data["bar_id"].duplicated().any():
            raise Mt5MarketDataProviderError(
                "MT5 candles contain duplicate bar IDs"
            )

        invalid_high_low = data["High"] < data["Low"]

        invalid_open = (
            (data["Open"] < data["Low"])
            | (data["Open"] > data["High"])
        )

        invalid_close = (
            (data["Close"] < data["Low"])
            | (data["Close"] > data["High"])
        )

        if invalid_high_low.any():
            raise Mt5MarketDataProviderError(
                "MT5 candles contain High values below Low"
            )

        if invalid_open.any():
            raise Mt5MarketDataProviderError(
                "MT5 candles contain Open values outside "
                "the Low-High range"
            )

        if invalid_close.any():
            raise Mt5MarketDataProviderError(
                "MT5 candles contain Close values outside "
                "the Low-High range"
            )

        if (data["Volume"] < 0).any():
            raise Mt5MarketDataProviderError(
                "MT5 candles contain negative volume"
            )

    def _build_provenance(
        self,
        *,
        specification: MarketExperimentSpecification,
        data: pd.DataFrame,
        start_at_utc: datetime,
        end_at_utc: datetime,
    ) -> dict[str, Any]:
        account_info = self._mt5.account_info()
        terminal_info = self._mt5.terminal_info()

        return {
            "data_source": "mt5",
            "broker_company": (
                account_info.company
                if account_info is not None
                else None
            ),
            "broker_server": (
                account_info.server
                if account_info is not None
                else None
            ),
            "symbol": specification.symbol,
            "timeframe": specification.timeframe,
            "requested_from_utc": start_at_utc.isoformat(),
            "requested_to_utc": end_at_utc.isoformat(),
            "actual_first_bar_utc": (
                data.index[0].isoformat()
            ),
            "actual_last_bar_utc": (
                data.index[-1].isoformat()
            ),
            "bars_count": len(data),
            "terminal_version": self._mt5.version(),
            "terminal_path": (
                terminal_info.path
                if terminal_info is not None
                else None
            ),
            "mt5_package_version": getattr(
                self._mt5,
                "__version__",
                None,
            ),
            "retrieved_at_utc": (
                self._to_utc(self._clock.now()).isoformat()
            ),
        }

    def _resolve_timeframe(
        self,
        timeframe: str,
    ) -> int:
        normalized = timeframe.strip().upper()

        timeframe_mapping = {
            "M1": self._mt5.TIMEFRAME_M1,
            "1M": self._mt5.TIMEFRAME_M1,
            "M5": self._mt5.TIMEFRAME_M5,
            "5M": self._mt5.TIMEFRAME_M5,
            "M15": self._mt5.TIMEFRAME_M15,
            "15M": self._mt5.TIMEFRAME_M15,
            "M30": self._mt5.TIMEFRAME_M30,
            "30M": self._mt5.TIMEFRAME_M30,
            "H1": self._mt5.TIMEFRAME_H1,
            "1H": self._mt5.TIMEFRAME_H1,
            "H4": self._mt5.TIMEFRAME_H4,
            "4H": self._mt5.TIMEFRAME_H4,
            "D1": self._mt5.TIMEFRAME_D1,
            "1D": self._mt5.TIMEFRAME_D1,
        }

        try:
            return timeframe_mapping[normalized]
        except KeyError as error:
            supported = ", ".join(
                sorted(timeframe_mapping)
            )

            raise Mt5MarketDataProviderError(
                f"Unsupported MT5 timeframe {timeframe!r}. "
                f"Supported values: {supported}"
            ) from error

    def _resolve_timeframe_duration(
        self,
        timeframe: str,
    ) -> timedelta:
        normalized = timeframe.strip().upper()

        duration_mapping = {
            "M1": timedelta(minutes=1),
            "1M": timedelta(minutes=1),
            "M5": timedelta(minutes=5),
            "5M": timedelta(minutes=5),
            "M15": timedelta(minutes=15),
            "15M": timedelta(minutes=15),
            "M30": timedelta(minutes=30),
            "30M": timedelta(minutes=30),
            "H1": timedelta(hours=1),
            "1H": timedelta(hours=1),
            "H4": timedelta(hours=4),
            "4H": timedelta(hours=4),
            "D1": timedelta(days=1),
            "1D": timedelta(days=1),
        }

        try:
            return duration_mapping[normalized]
        except KeyError as error:
            raise Mt5MarketDataProviderError(
                f"Unsupported MT5 timeframe {timeframe!r}"
            ) from error

    def _to_utc(
        self,
        value: datetime,
    ) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)

        return value.astimezone(timezone.utc)

    def _format_mt5_error(
        self,
        message: str,
    ) -> str:
        return (
            f"{message}. "
            f"MT5 last_error={self._mt5.last_error()!r}"
        )