from unittest.mock import Mock

import pandas as pd

from src.application.simple_market_signal_provider import (
    SimpleMarketSignalProvider,
)


def test_simple_provider_uses_canonical_close_column() -> None:
    provider = SimpleMarketSignalProvider()

    data = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(
                [
                    "2024-01-01",
                    "2024-01-02",
                    "2024-01-03",
                ]
            ),
            "open": [100.0, 101.0, 100.0],
            "high": [102.0, 103.0, 102.0],
            "low": [99.0, 100.0, 98.0],
            "close": [100.0, 101.0, 99.0],
            "tick_volume": [10, 11, 12],
        }
    )

    result = provider.generate(
        data=data,
        specification=Mock(),
    )

    assert result["AI_prediction"].tolist() == [0, 1, -1]