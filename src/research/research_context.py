from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

import pandas as pd

from src.research.assumption import (
    AssumptionSet,
)
from src.research.research_environment import (
    ResearchEnvironmentRef,
)


SpecificationT = TypeVar("SpecificationT")


@dataclass(frozen=True)
class ResearchContext(Generic[SpecificationT]):
    """
    Immutable execution context for one research experiment.

    Every research cycle operates inside one immutable context.
    """

    specification: SpecificationT

    environment: ResearchEnvironmentRef

    market_data: pd.DataFrame

    assumptions: AssumptionSet

    def __post_init__(self) -> None:
        if self.market_data.empty:
            raise ValueError(
                "market_data cannot be empty"
            )

        required_attrs = (
            "dataset_fingerprint",
        )

        missing = [
            attr
            for attr in required_attrs
            if attr not in self.market_data.attrs
        ]

        if missing:
            raise ValueError(
                "ResearchContext requires a "
                "fingerprinted canonical dataset. "
                f"Missing attrs: {missing}"
            )

        if (
            self.environment.dataset_fingerprint
            != self.market_data.attrs[
                "dataset_fingerprint"
            ]
        ):
            raise ValueError(
                "ResearchEnvironmentRef does not "
                "match supplied market dataset."
            )