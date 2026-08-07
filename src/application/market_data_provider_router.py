from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType

import pandas as pd

from src.application.market_data_provider import (
    LegacyMarketDataProvider,
)
from src.application.market_experiment_specification import (
    MarketExperimentSpecification,
)


class MarketDataProviderRouter:
    """Route a specification to its registered data source."""

    def __init__(
        self,
        providers: Mapping[str, LegacyMarketDataProvider],
    ) -> None:
        if not isinstance(providers, Mapping):
            raise TypeError("providers must be a mapping")

        normalized = {}

        for source, provider in providers.items():
            if not isinstance(source, str):
                raise TypeError(
                    "provider source must be a string"
                )

            key = source.strip().lower()

            if not key:
                raise ValueError(
                    "provider source must not be empty"
                )

            if key in normalized:
                raise ValueError(
                    "provider sources must be unique "
                    "after normalization"
                )

            if not callable(getattr(provider, "load", None)):
                raise TypeError(
                    "provider must provide a callable "
                    "load method"
                )

            normalized[key] = provider

        if not normalized:
            raise ValueError(
                "providers must not be empty"
            )

        self._providers = MappingProxyType(normalized)

    def load(
        self,
        specification: MarketExperimentSpecification,
    ) -> pd.DataFrame:
        if not isinstance(
            specification,
            MarketExperimentSpecification,
        ):
            raise TypeError(
                "specification must be a "
                "MarketExperimentSpecification"
            )

        source = specification.data_source.strip().lower()
        provider = self._providers.get(source)

        if provider is None:
            registered = ", ".join(
                sorted(self._providers)
            )
            raise ValueError(
                f"unsupported market data source: "
                f"{source!r}; registered sources: "
                f"{registered}"
            )

        return provider.load(specification)
