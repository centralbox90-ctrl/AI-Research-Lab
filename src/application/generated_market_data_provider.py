import json
from datetime import datetime, timezone
from hashlib import sha256

import pandas as pd

from src.application.market_data_provider import (
    LegacyMarketDataProvider,
)
from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
)
from src.data.loader import generate_market_data


class GeneratedMarketDataProvider(
    LegacyMarketDataProvider,
):
    """
    Provides deterministic development market data.

    This adapter wraps the existing market-data generator and exposes it
    through the LegacyMarketDataProvider application boundary.

    It does not create signals, execute trades, or run experiments.
    """

    def load(
        self,
        specification: MarketExperimentSpecification,
    ) -> pd.DataFrame:
        """
        Load generated market data for one experiment.
        """

        return generate_market_data(
            symbol=specification.symbol,
            timeframe=specification.timeframe,
            start_at=specification.start_at,
            end_at=specification.end_at,
            random_seed=self._build_random_seed(
                specification
            ),
        )

    @classmethod
    def _build_random_seed(
        cls,
        specification: MarketExperimentSpecification,
    ) -> int:
        data_identity = {
            "schema_version": 1,
            "data_source": (
                specification.data_source.strip()
            ),
            "symbol": specification.symbol.strip(),
            "timeframe": (
                specification.timeframe.strip()
            ),
            "start_at": cls._serialize_timestamp(
                specification.start_at
            ),
            "end_at": cls._serialize_timestamp(
                specification.end_at
            ),
        }
        serialized = json.dumps(
            data_identity,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )
        digest = sha256(
            serialized.encode("utf-8")
        ).digest()

        return int.from_bytes(
            digest[:8],
            byteorder="big",
            signed=False,
        )

    @staticmethod
    def _serialize_timestamp(
        value: datetime,
    ) -> str:
        if (
            value.tzinfo is not None
            and value.utcoffset() is not None
        ):
            value = value.astimezone(
                timezone.utc
            )

        return value.isoformat()