from datetime import datetime, UTC
from types import SimpleNamespace

import pandas as pd

from src.application.mt5_market_data_provider import (
    Mt5MarketDataProvider,
)


class StubClock:

    def __init__(self, current_time: datetime) -> None:
        self._current_time = current_time

    def now(self) -> datetime:
        return self._current_time


class StubMt5Module:

    __version__ = "5.0-test"

    def account_info(self):
        return SimpleNamespace(
            company="Test Broker",
            server="Test Server",
        )

    def terminal_info(self):
        return SimpleNamespace(
            path=r"C:\Test\terminal.exe",
        )

    def version(self):
        return (5, 0, 1)


def test_mt5_market_data_provider_uses_clock_for_retrieval_time():

    retrieved_at = datetime(
        2026,
        7,
        17,
        14,
        30,
        tzinfo=UTC,
    )

    provider = Mt5MarketDataProvider(
        mt5_module=StubMt5Module(),
        clock=StubClock(retrieved_at),
    )

    specification = SimpleNamespace(
        symbol="EURUSD",
        timeframe="H1",
    )

    start_at = datetime(
        2026,
        7,
        1,
        tzinfo=UTC,
    )
    end_at = datetime(
        2026,
        7,
        2,
        tzinfo=UTC,
    )

    data = pd.DataFrame(
        {
            "Close": [1.1],
        },
        index=pd.DatetimeIndex(
            [
                datetime(
                    2026,
                    7,
                    1,
                    12,
                    tzinfo=UTC,
                )
            ]
        ),
    )

    provenance = provider._build_provenance(
        specification=specification,
        data=data,
        start_at_utc=start_at,
        end_at_utc=end_at,
    )

    assert provenance["retrieved_at_utc"] == (
        "2026-07-17T14:30:00+00:00"
    )
    assert provenance["data_source"] == "mt5"
    assert provenance["broker_company"] == "Test Broker"
    assert provenance["broker_server"] == "Test Server"
