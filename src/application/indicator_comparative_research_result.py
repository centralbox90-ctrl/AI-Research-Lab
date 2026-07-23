from __future__ import annotations

from dataclasses import dataclass

from src.application.market_dataset_quality import (
    DataQualityReport,
)
from src.research.comparative_analysis import (
    ComparativeAnalysis,
)
from src.research.market_dataset_fingerprint import (
    MarketDatasetFingerprint,
)
from src.research.specification import (
    ResearchSpecification,
)


@dataclass(frozen=True, slots=True)
class IndicatorComparativeResearchResult:
    """Reproducible result of comparative indicator research."""

    indicator_id: str
    symbol: str
    timeframe: str
    research_specification: ResearchSpecification
    dataset_fingerprint: MarketDatasetFingerprint
    data_quality_report: DataQualityReport
    analysis: ComparativeAnalysis

    def __post_init__(self) -> None:
        indicator_id = self._normalize_text(
            self.indicator_id,
            field_name="indicator_id",
        )
        symbol = self._normalize_text(
            self.symbol,
            field_name="symbol",
            uppercase=True,
        )
        timeframe = self._normalize_text(
            self.timeframe,
            field_name="timeframe",
            uppercase=True,
        )

        if not isinstance(
            self.research_specification,
            ResearchSpecification,
        ):
            raise TypeError(
                "research_specification must be a "
                "ResearchSpecification"
            )

        if (
            self.research_specification
            .indicator
            .indicator_id
            != indicator_id
        ):
            raise ValueError(
                "indicator_id must match the "
                "research specification"
            )

        if not isinstance(
            self.dataset_fingerprint,
            MarketDatasetFingerprint,
        ):
            raise TypeError(
                "dataset_fingerprint must be a "
                "MarketDatasetFingerprint"
            )

        if not isinstance(
            self.data_quality_report,
            DataQualityReport,
        ):
            raise TypeError(
                "data_quality_report must be a "
                "DataQualityReport"
            )

        if not isinstance(
            self.analysis,
            ComparativeAnalysis,
        ):
            raise TypeError(
                "analysis must be a ComparativeAnalysis"
            )

        object.__setattr__(
            self,
            "indicator_id",
            indicator_id,
        )
        object.__setattr__(
            self,
            "symbol",
            symbol,
        )
        object.__setattr__(
            self,
            "timeframe",
            timeframe,
        )

    @property
    def research_fingerprint(self) -> str:
        return self.research_specification.fingerprint

    @property
    def dataset_id(self) -> str:
        return (
            self.dataset_fingerprint
            .dataset_fingerprint
        )

    @staticmethod
    def _normalize_text(
        value: object,
        *,
        field_name: str,
        uppercase: bool = False,
    ) -> str:
        if not isinstance(value, str):
            raise TypeError(
                f"{field_name} must be a string"
            )

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                f"{field_name} must not be empty"
            )

        if uppercase:
            return normalized.upper()

        return normalized
